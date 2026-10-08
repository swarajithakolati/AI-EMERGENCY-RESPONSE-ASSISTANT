#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "  AI EMERGENCY RESPONSE ASSISTANT"
echo "  “Helping emergency responders understand incoming information faster.”"
echo "=========================================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Check Python environment
echo "[1/4] Starting FastAPI backend on http://localhost:8000..."
export PYTHONPATH="$PROJECT_ROOT/backend"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cleanup() {
  echo ""
  echo "Shutting down AI Emergency Response Assistant services..."
  kill $BACKEND_PID 2>/dev/null || true
  exit 0
}
trap cleanup SIGINT SIGTERM EXIT

sleep 2

echo "[2/4] Starting Vite React Frontend on http://localhost:5173..."
cd "$PROJECT_ROOT/frontend"
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!

echo ""
echo "=========================================================="
echo "  SERVICES ONLINE"
echo "  - Control Dashboard: http://localhost:5173"
echo "  - FastAPI Swagger:   http://localhost:8000/docs"
echo "  - Acceptance Tests:  PYTHONPATH=backend pytest backend/app/tests/test_acceptance.py"
echo "=========================================================="
echo ""

wait $FRONTEND_PID
