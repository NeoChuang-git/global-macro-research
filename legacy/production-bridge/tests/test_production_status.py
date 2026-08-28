import json
import plistlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS_SCRIPT = ROOT / "scripts" / "production_status.py"


class ProductionStatusCliTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source_repo = self.root / "source"
        self.production_repo = self.root / "production"
        self.drive_root = self.root / "drive"
        self.inbox = self.drive_root / "inbox" / "production"
        self.plist_path = self.root / "production.plist"
        self.launchctl_path = self.root / "launchctl.txt"
        self.stdout_path = self.root / "stdout.log"
        self.stderr_path = self.root / "stderr.log"

        self.source_repo.mkdir()
        self.inbox.mkdir(parents=True)
        (self.production_repo / "rules").mkdir(parents=True)
        (self.production_repo / "runtime" / "logs").mkdir(parents=True)
        (self.production_repo / "runtime" / "state").mkdir(parents=True)
        (self.production_repo / "reports" / "production").mkdir(parents=True)
        (self.production_repo / "data" / "signals" / "production").mkdir(
            parents=True
        )

        self._write_plist()
        self._write_launchctl_snapshot()
        self._write_empty_runtime()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_plist(self):
        content = {
            "Label": "com.globalmacro.production-bridge",
            "ProgramArguments": ["/tmp/globalmacro-production-bridge"],
            "StartCalendarInterval": [
                {"Minute": 5},
                {"Minute": 20},
                {"Minute": 35},
                {"Minute": 50},
            ],
        }
        self.plist_path.write_bytes(plistlib.dumps(content))

    def _write_launchctl_snapshot(self):
        self.launchctl_path.write_text(
            "\n".join(
                [
                    "state = not running",
                    "runs = 3",
                    "last exit code = 0",
                ]
            ),
            encoding="utf-8",
        )

    def _write_empty_runtime(self):
        config = {
            "drive_root": str(self.drive_root),
            "environments": {"production": {"inbox": "inbox/production"}},
        }
        (self.production_repo / "rules" / "drive-bridge-config.json").write_text(
            json.dumps(config),
            encoding="utf-8",
        )
        (self.production_repo / "runtime" / "logs" / "production-bridge.log").write_text(
            "\n".join(
                [
                    "2026-08-20 21:23:47 ===== production bridge start pid=42 =====",
                    "[INFO] production: no payloads",
                    "2026-08-20 21:24:08 ===== production bridge end status=0 =====",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (self.production_repo / "runtime" / "state" / "processed-events.jsonl").touch()
        (self.production_repo / "data" / "signals" / "production" / "signal-history.jsonl").touch()
        self.stdout_path.touch()
        self.stderr_path.touch()

    def _run_status(self):
        result = subprocess.run(
            [
                "/usr/bin/python3",
                str(STATUS_SCRIPT),
                "--json",
                "--plist",
                str(self.plist_path),
                "--source-repo",
                str(self.source_repo),
                "--production-repo",
                str(self.production_repo),
                "--launchctl-snapshot",
                str(self.launchctl_path),
                "--stdout-log",
                str(self.stdout_path),
                "--stderr-log",
                str(self.stderr_path),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_reports_healthy_empty_queue_without_claiming_publish_success(self):
        report = self._run_status()

        self.assertEqual(report["scheduler"]["status"], "PASS")
        self.assertEqual(report["queue"]["status"], "PASS")
        self.assertEqual(report["queue"]["payload_count"], 0)
        self.assertEqual(report["queue"]["html_count"], 0)
        self.assertEqual(report["publish"]["status"], "UNVERIFIED")
        self.assertEqual(report["publish"]["verified_event_ids"], [])

    def test_reports_publish_only_when_all_event_evidence_matches(self):
        event_id = "production-early_warning-20260820T213500-smoke"
        runtime_root = self.production_repo / "runtime"
        report_root = self.production_repo / "reports" / "production" / "early-warning"
        history_path = (
            self.production_repo
            / "data"
            / "signals"
            / "production"
            / "signal-history.jsonl"
        )

        (runtime_root / "state" / "processed-events.jsonl").write_text(
            json.dumps(
                {
                    "event_id": event_id,
                    "environment": "production",
                    "processed_at": "2026-08-20T13:36:00+00:00",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (runtime_root / "logs" / "production-bridge.log").write_text(
            "\n".join(
                [
                    "2026-08-20 21:35:00 ===== production bridge start pid=43 =====",
                    f"[OK] published: {event_id}",
                    "2026-08-20 21:35:20 ===== production bridge end status=0 =====",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        history_path.write_text(
            json.dumps({"event_id": event_id, "environment": "production"}) + "\n",
            encoding="utf-8",
        )
        report_root.mkdir(parents=True)
        (report_root / f"{event_id}.html").write_text("<html></html>", encoding="utf-8")
        (report_root / f"{event_id}.metadata.json").write_text(
            json.dumps({"event_id": event_id, "environment": "production"}),
            encoding="utf-8",
        )

        report = self._run_status()

        self.assertEqual(report["publish"]["status"], "PASS")
        self.assertEqual(report["publish"]["verified_event_ids"], [event_id])


if __name__ == "__main__":
    unittest.main()
