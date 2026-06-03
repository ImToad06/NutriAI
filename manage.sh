#!/bin/bash

# Script para gestionar la WebApp NutriIA (Backend FastAPI + Frontend estático)
# Uso: ./manage.sh [start|stop|restart|status]

VENV_BIN="./.venv/bin"
BACKEND_PID_FILE=".backend.pid"
FRONTEND_PID_FILE=".frontend.pid"
BACKEND_LOG="backend.log"
FRONTEND_LOG="frontend.log"
BACKEND_PORT=8000
FRONTEND_PORT=5500

start_backend() {
    if [ -f "$BACKEND_PID_FILE" ] && ps -p $(cat "$BACKEND_PID_FILE") > /dev/null 2>&1; then
        echo "⚠️  Backend ya está corriendo (PID: $(cat "$BACKEND_PID_FILE"))."
        return 0
    fi

    echo "🚀 Iniciando NutriIA Backend..."

    if [ ! -d ".venv" ]; then
        echo "❌ Error: No se encontró el entorno virtual (.venv)."
        echo "Ejecuta: python3 -m venv .venv && pip install -r requirements.txt"
        return 1
    fi

    setsid nohup "$VENV_BIN/uvicorn" backend.main:app --host 0.0.0.0 --port "$BACKEND_PORT" \
        > "$BACKEND_LOG" 2>&1 < /dev/null &
    echo $! > "$BACKEND_PID_FILE"

    sleep 2
    if ps -p $(cat "$BACKEND_PID_FILE") > /dev/null 2>&1; then
        echo "✅ Backend iniciado (PID: $(cat "$BACKEND_PID_FILE"))."
        echo "   🔗 API:   http://localhost:$BACKEND_PORT"
        echo "   🔗 Docs:  http://localhost:$BACKEND_PORT/docs"
    else
        echo "❌ Error al iniciar el backend. Revisa $BACKEND_LOG"
        rm -f "$BACKEND_PID_FILE"
        return 1
    fi
}

start_frontend() {
    if [ -f "$FRONTEND_PID_FILE" ] && ps -p $(cat "$FRONTEND_PID_FILE") > /dev/null 2>&1; then
        echo "⚠️  Frontend ya está corriendo (PID: $(cat "$FRONTEND_PID_FILE"))."
        return 0
    fi

    echo "🌐 Iniciando NutriIA Frontend..."

    if [ ! -d "frontend" ]; then
        echo "❌ Error: No se encontró el directorio 'frontend/'."
        return 1
    fi

    setsid nohup "$VENV_BIN/python" -m http.server "$FRONTEND_PORT" --directory frontend \
        > "$FRONTEND_LOG" 2>&1 < /dev/null &
    echo $! > "$FRONTEND_PID_FILE"

    sleep 1
    if ps -p $(cat "$FRONTEND_PID_FILE") > /dev/null 2>&1; then
        echo "✅ Frontend iniciado (PID: $(cat "$FRONTEND_PID_FILE"))."
        echo "   🔗 App:   http://localhost:$FRONTEND_PORT"
    else
        echo "❌ Error al iniciar el frontend. Revisa $FRONTEND_LOG"
        rm -f "$FRONTEND_PID_FILE"
        return 1
    fi
}

start() {
    start_backend
    local rc_backend=$?
    start_frontend
    local rc_frontend=$?

    if [ $rc_backend -eq 0 ] && [ $rc_frontend -eq 0 ]; then
        echo ""
        echo "📄 Logs backend:  tail -f $BACKEND_LOG"
        echo "📄 Logs frontend: tail -f $FRONTEND_LOG"
    fi
}

stop_backend() {
    if [ -f "$BACKEND_PID_FILE" ]; then
        local pid
        pid=$(cat "$BACKEND_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "🛑 Deteniendo Backend (PID: $pid)..."
            kill "$pid" 2>/dev/null
            sleep 1
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null
            fi
        fi
        rm -f "$BACKEND_PID_FILE"
    fi

    local orphans
    orphans=$(pgrep -f "uvicorn backend.main:app" 2>/dev/null)
    if [ -n "$orphans" ]; then
        echo "🔍 Limpiando procesos huérfanos del backend: $orphans"
        kill $orphans 2>/dev/null
    fi
}

stop_frontend() {
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local pid
        pid=$(cat "$FRONTEND_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "🛑 Deteniendo Frontend (PID: $pid)..."
            kill "$pid" 2>/dev/null
            sleep 1
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null
            fi
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi

    local orphans
    orphans=$(pgrep -f "http.server $FRONTEND_PORT" 2>/dev/null)
    if [ -n "$orphans" ]; then
        echo "🔍 Limpiando procesos huérfanos del frontend: $orphans"
        kill $orphans 2>/dev/null
    fi
}

stop() {
    stop_backend
    echo "✅ Backend detenido."
    stop_frontend
    echo "✅ Frontend detenido."
}

status() {
    echo "=== Backend (puerto $BACKEND_PORT) ==="
    if [ -f "$BACKEND_PID_FILE" ] && ps -p $(cat "$BACKEND_PID_FILE") > /dev/null 2>&1; then
        echo "🟢 CORRIENDO (PID: $(cat "$BACKEND_PID_FILE"))"
        echo "   🔗 http://localhost:$BACKEND_PORT"
        echo "   🔗 http://localhost:$BACKEND_PORT/docs"
    else
        echo "🔴 DETENIDO"
    fi

    echo ""
    echo "=== Frontend (puerto $FRONTEND_PORT) ==="
    if [ -f "$FRONTEND_PID_FILE" ] && ps -p $(cat "$FRONTEND_PID_FILE") > /dev/null 2>&1; then
        echo "🟢 CORRIENDO (PID: $(cat "$FRONTEND_PID_FILE"))"
        echo "   🔗 http://localhost:$FRONTEND_PORT"
    else
        echo "🔴 DETENIDO"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 1
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status}"
        exit 1
esac
