#!/bin/bash

echo "========================================="
echo "  VERIFICADOR DE ESTADO DEL SISTEMA"
echo "========================================="

echo ""
echo "[1] Estado del contenedor:"
docker ps --filter "name=escuela_asistencias" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "[2] Últimos logs (sin errores):"
docker logs --tail 10 escuela_asistencias 2>&1 | grep -v "ERROR" | tail -5

echo ""
echo "[3] Archivos dentro del contenedor:"
echo "  - Base de datos:"
docker exec escuela_asistencias ls -la /app/data/ 2>/dev/null || echo "    ❌ No se puede acceder"
echo "  - Uploads:"
docker exec escuela_asistencias ls -la /app/uploads/ 2>/dev/null || echo "    ❌ No se puede acceder"

echo ""
echo "[4] Ubicación física de los volúmenes en el host:"
docker volume inspect escuela_test_app_data --format "  app_data: {{.Mountpoint}}"
docker volume inspect escuela_test_uploads_data --format "  uploads_data: {{.Mountpoint}}"

echo ""
echo "[5] Conteo de archivos PDF dentro del contenedor:"
PDF_COUNT=$(docker exec escuela_asistencias find /app/uploads -name "*.pdf" 2>/dev/null | wc -l)
echo "  PDFs encontrados: $PDF_COUNT"

echo ""
echo "[6] Resumen de la base de datos (desde el contenedor):"
docker exec escuela_asistencias sqlite3 /app/data/school.db "SELECT name FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "  ❌ No se puede leer la BD"

echo ""
echo "[7] Usuarios registrados:"
docker exec escuela_asistencias sqlite3 /app/data/school.db "SELECT username, role FROM user;" 2>/dev/null || echo "  ❌ No se pueden leer usuarios"

echo ""
echo "[8] Backups disponibles:"
docker exec escuela_asistencias sqlite3 /app/data/school.db "SELECT description FROM backup;" 2>/dev/null || echo "  ❌ No se pueden leer backups"

echo ""
echo "[9] Últimos archivos subidos (5 más recientes):"
docker exec escuela_asistencias ls -lt /app/uploads/ 2>/dev/null | head -6 | tail -5 || echo "  ❌ No hay archivos"

echo ""
echo "========================================="
echo "  FIN DE LA VERIFICACIÓN"
echo "========================================="
