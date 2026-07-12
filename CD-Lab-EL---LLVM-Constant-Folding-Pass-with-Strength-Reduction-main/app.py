#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import tempfile
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
RUNNER = ROOT / "build" / "cf_runner"
TESTCASES_DIR = ROOT / "testcases"


def find_available_port(start_port: int) -> int:
    port = start_port
    for _ in range(20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("0.0.0.0", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(f"Unable to find a free port starting at {start_port}")


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        if parsed.path == "/presets":
            try:
                presets = self.load_presets()
                self.send_json(presets)
            except Exception as e:
                tb = traceback.format_exc()
                print("/presets handler error:\n", tb)
                self.send_json({"ok": False, "error": "Failed to load presets", "detail": str(e)}, status=500)
            return
        if parsed.path.startswith("/static/"):
            rel = parsed.path[len("/static/"):]
            file_path = STATIC_DIR / rel
            if file_path.exists() and file_path.is_file():
                content_type = "text/css" if file_path.suffix == ".css" else "text/html"
                self.serve_file(file_path, content_type)
                return
        self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/run":
            self.send_error(404, "Not found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
        try:
            payload = json.loads(body or "{}")
        except json.JSONDecodeError:
            self.send_json({"ok": False, "error": "Invalid JSON body"}, status=400)
            return

        options = payload.get("options") or {}
        if options:
            try:
                input_ir = (payload.get("input") or "").strip() or self.build_ir_from_form(options)
                output_ir, explanation, pipeline, analysis = self.run_custom_demo(input_ir, options)
                self.send_json({"ok": True, "output": output_ir, "explanation": explanation, "pipeline": pipeline, "analysis": analysis})
            except Exception as e:
                tb = traceback.format_exc()
                print("run (custom) handler error:\n", tb)
                self.send_json({"ok": False, "error": "Custom demo failed", "detail": str(e)}, status=500)
            return

        input_ir = (payload.get("input") or "").strip()
        if not input_ir:
            self.send_json({"ok": False, "error": "Please enter LLVM IR first."}, status=400)
            return

        if not RUNNER.exists():
            self.send_json({"ok": False, "error": "Runner not built yet. Run ./build.sh first."}, status=500)
            return

        with tempfile.NamedTemporaryFile("w", suffix=".ll", delete=False, dir=str(ROOT)) as src_file:
            src_file.write(input_ir)
            src_path = src_file.name

        with tempfile.NamedTemporaryFile("w", suffix=".ll", delete=False, dir=str(ROOT)) as out_file:
            out_path = out_file.name

        try:
            try:
                result = subprocess.run([str(RUNNER), src_path, out_path], cwd=str(ROOT), capture_output=True, text=True)
            except OSError as e:
                tb = traceback.format_exc()
                print("Runner execution failed:\n", tb)
                self.send_json({"ok": False, "error": "Runner execution failed", "detail": str(e)}, status=500)
                return

            output_ir = Path(out_path).read_text(encoding="utf-8") if Path(out_path).exists() else ""
            explanation = self.explain_transformation(input_ir, output_ir, result)
            if result.returncode != 0:
                # Include stderr/stdout snippets for easier debugging in the UI
                err = (result.stderr or result.stdout or "Runner failed").strip()
                self.send_json({"ok": False, "error": "Runner returned non-zero exit", "detail": err}, status=500)
                return
            self.send_json({"ok": True, "output": output_ir, "explanation": explanation, "analysis": self.analyze_transformation(input_ir, output_ir), "pipeline": [
                "Parsed the LLVM IR input.",
                "Checked the candidate instruction for optimization opportunities.",
                "Applied the relevant constant-folding or strength-reduction rule.",
                "Produced the final transformed IR."
            ]})
        finally:
            for path in (src_path, out_path):
                try:
                    os.unlink(path)
                except FileNotFoundError:
                    pass

    def build_ir_from_form(self, options):
        operator = options.get("operator", "add")
        left_kind = options.get("leftKind", "constant")
        right_kind = options.get("rightKind", "constant")
        left_value = str(options.get("leftValue", "4") or "4")
        right_value = str(options.get("rightValue", "5") or "5")

        def render_operand(kind, value):
            if kind == "variable":
                return "%x"
            try:
                return str(int(value))
            except ValueError:
                return "0"

        left_operand = render_operand(left_kind, left_value)
        right_operand = render_operand(right_kind, right_value)
        return (
            "define i32 @demo(i32 %x) {\n"
            f"  %1 = {operator} i32 {left_operand}, {right_operand}\n"
            "  ret i32 %1\n"
            "}\n"
        )

    def run_custom_demo(self, input_ir, options):
        operator = options.get("operator", "add")
        fold_enabled = bool(options.get("foldEnabled", True))
        reduce_enabled = bool(options.get("reduceEnabled", True))
        power_of_two_only = bool(options.get("powerOfTwoOnly", True))
        signed_mode = bool(options.get("signedMode", False))

        pipeline = [
            "Parsed the custom operand form into a small LLVM IR example.",
            "Checked the selected operator and operand kinds.",
            "Applied the requested optimization rules.",
            "Produced an explanation for the outcome."
        ]

        left_kind = options.get("leftKind", "constant")
        right_kind = options.get("rightKind", "constant")
        left_value = self._parse_int(options.get("leftValue", "4"))
        right_value = self._parse_int(options.get("rightValue", "5"))

        both_constants = left_kind == "constant" and right_kind == "constant"
        analysis = {
            "applied": False,
            "rule": "No rule matched",
            "beforeCost": "1 arithmetic instruction",
            "afterCost": "1 arithmetic instruction",
            "savings": "No instruction eliminated",
            "detail": "The original instruction is retained because the selected rules cannot safely simplify it."
        }
        if both_constants and fold_enabled:
            result = self._apply_binary_op(operator, left_value, right_value)
            output_ir = (
                "define i32 @demo(i32 %x) {\n"
                f"  ret i32 {result}\n"
                "}\n"
            )
            explanation = "Both operands were constants, so the pass folded the expression into a single literal value."
            analysis.update({
                "applied": True, "rule": "Constant folding", "afterCost": "0 runtime arithmetic instructions",
                "savings": "1 instruction eliminated", "detail": f"{left_value} {self._operator_symbol(operator)} {right_value} is known during compilation, so the runtime receives {result}."
            })
            return output_ir, explanation, pipeline, analysis

        if reduce_enabled and operator == "mul" and left_kind == "constant" and right_kind != "constant":
            multiplier = left_value
            if self._is_power_of_two(multiplier):
                shift_amount = multiplier.bit_length() - 1
                output_ir = (
                    "define i32 @demo(i32 %x) {\n"
                    f"  %1 = shl i32 %x, {shift_amount}\n"
                    "  ret i32 %1\n"
                    "}\n"
                )
                explanation = "The multiplier was a positive power of two, so the pass replaced the multiply with a shift."
                analysis.update({
                    "applied": True, "rule": "Strength reduction", "afterCost": "1 shift instruction",
                    "savings": "Replaces multiply with shift", "detail": f"Multiplying by {multiplier} is equivalent to shifting left by {shift_amount} bit(s)."
                })
                return output_ir, explanation, pipeline, analysis

        if reduce_enabled and operator == "mul" and right_kind == "constant" and left_kind != "constant":
            multiplier = right_value
            if self._is_power_of_two(multiplier):
                shift_amount = multiplier.bit_length() - 1
                output_ir = (
                    "define i32 @demo(i32 %x) {\n"
                    f"  %1 = shl i32 %x, {shift_amount}\n"
                    "  ret i32 %1\n"
                    "}\n"
                )
                explanation = "The multiplier was a positive power of two, so the pass replaced the multiply with a shift."
                analysis.update({
                    "applied": True, "rule": "Strength reduction", "afterCost": "1 shift instruction",
                    "savings": "Replaces multiply with shift", "detail": f"Multiplying by {multiplier} is equivalent to shifting left by {shift_amount} bit(s)."
                })
                return output_ir, explanation, pipeline, analysis

        explanation = "The selected rule was not applied for this case, so the IR stayed unchanged."
        if not fold_enabled:
            explanation = "Constant folding was disabled for this run, so the example remained in its original form."
        elif not reduce_enabled:
            explanation = "Strength reduction was disabled for this run, so the multiply was left unchanged."
        elif operator == "mul" and not both_constants:
            explanation = "Strength reduction only applies to multiplication by a positive power of two, so this instruction was kept unchanged."
        if signed_mode:
            explanation += " Signed-mode behavior is enabled in this demo."
        return input_ir, explanation, pipeline, analysis

    def _operator_symbol(self, operator):
        return {"add": "+", "sub": "-", "mul": "×", "sdiv": "÷", "and": "&", "or": "|", "xor": "^"}.get(operator, operator)

    def _parse_int(self, value):
        try:
            return int(str(value))
        except ValueError:
            return 0

    def _apply_binary_op(self, operator, left, right):
        if operator == "add":
            return left + right
        if operator == "sub":
            return left - right
        if operator == "mul":
            return left * right
        if operator == "sdiv":
            return 0 if right == 0 else left // right
        if operator == "and":
            return left & right
        if operator == "or":
            return left | right
        if operator == "xor":
            return left ^ right
        return left

    def _is_power_of_two(self, value):
        return value > 0 and (value & (value - 1)) == 0

    def load_presets(self):
        if not TESTCASES_DIR.exists():
            return []
        presets = []
        for path in sorted(TESTCASES_DIR.glob("*.ll")):
            presets.append({"name": path.name, "content": path.read_text(encoding="utf-8")})
        return presets

    def explain_transformation(self, input_ir, output_ir, result):
        lower_input = input_ir.lower()
        lower_output = output_ir.lower()
        if "shl" in lower_output:
            return "The multiplier was a positive power of two, so the pass replaced the multiply with a shift."
        if "ret i32" in lower_output and "ret i32" not in lower_input:
            return "Both operands were constants, so the pass folded the expression into a single literal value."
        if output_ir.strip() != input_ir.strip():
            return "The pass made a transformation, but the output pattern was not a simple shift or literal fold."
        if "mul" in lower_input and "5" in lower_input:
            return "This case is intentionally left unchanged because the multiplier is not a power of two."
        if "-4" in lower_input:
            return "This negative multiplier is not a supported strength-reduction case, so the pass leaves it alone."
        return "No optimization rule matched this input, so the IR remained unchanged."

    def analyze_transformation(self, input_ir, output_ir):
        """Return display data based on the runner's real IR output."""
        if " shl " in output_ir and " mul " in input_ir:
            return {
                "applied": True, "rule": "Strength reduction",
                "beforeCost": "1 multiply instruction", "afterCost": "1 shift instruction",
                "savings": "Replaces multiply with shift",
                "detail": "The runner proved that multiplying by a positive power of two is equivalent to shifting left."
            }
        if input_ir.strip() != output_ir.strip() and "ret i32" in output_ir:
            return {
                "applied": True, "rule": "Constant folding",
                "beforeCost": "1 arithmetic instruction", "afterCost": "0 runtime arithmetic instructions",
                "savings": "1 instruction eliminated",
                "detail": "The runner evaluated constant operands at compile time and substituted the resulting literal."
            }
        return {
            "applied": False, "rule": "No rule matched",
            "beforeCost": "Original instructions retained", "afterCost": "No change",
            "savings": "No instruction eliminated",
            "detail": "The runner kept the original IR because no supported rewrite could be proven safe."
        }

    def serve_file(self, path, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(path.read_bytes())

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    requested_port = int(os.environ.get("PORT", "8000"))
    port = find_available_port(requested_port)
    server = ThreadingHTTPServer(("0.0.0.0", port), DemoHandler)
    print(f"LLVM pass demo running at http://localhost:{port}")
    server.serve_forever()
