#!/bin/bash
# Script para verificar y arreglar el servicio appo.service

echo "🔍 Verificando servicio appo.service..."

# 1. Ver el contenido del archivo de servicio
echo "📄 Contenido del archivo appo.service:"
sudo cat /etc/systemd/system/appo.service

echo ""
echo "🔍 Verificando qué puerto está usando..."
sudo grep -E "bind|8015|8016|8000" /etc/systemd/system/appo.service

echo ""
echo "📊 Estado del servicio appo:"
sudo systemctl status appo --no-pager -l

echo ""
echo "🔍 Verificando qué puerto está usando realmente (netstat):"
sudo netstat -tulpn | grep -E "8015|8016|8000" | grep python

echo ""
echo "🛑 Deteniendo servicio appo..."
sudo systemctl stop appo

echo ""
echo "✏️  Actualizando puerto a 8016 en appo.service..."
sudo sed -i 's/:8000/:8016/g' /etc/systemd/system/appo.service
sudo sed -i 's/:8015/:8016/g' /etc/systemd/system/appo.service
sudo sed -i 's/127.0.0.1:8000/127.0.0.1:8016/g' /etc/systemd/system/appo.service
sudo sed -i 's/127.0.0.1:8015/127.0.0.1:8016/g' /etc/systemd/system/appo.service

echo ""
echo "✅ Archivo actualizado. Verificando cambios:"
sudo grep -E "bind|8016" /etc/systemd/system/appo.service

echo ""
echo "🔄 Recargando systemd..."
sudo systemctl daemon-reload

echo ""
echo "🚀 Iniciando servicio appo..."
sudo systemctl start appo

echo ""
echo "⏳ Esperando 3 segundos..."
sleep 3

echo ""
echo "📊 Estado final del servicio:"
sudo systemctl status appo --no-pager -l

echo ""
echo "🔍 Verificando puerto 8016 en uso:"
sudo netstat -tulpn | grep 8016

echo ""
echo "✅ ¡Completado!"


