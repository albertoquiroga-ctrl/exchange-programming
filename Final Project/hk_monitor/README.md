# HK Conditions Monitor (versión para principiantes)

Todo ya viene con valores por defecto dentro del código. No hay archivos TOML ni base de datos que tocar.

## Cómo probar
```bash
cd hk_monitor
python -m hk_monitor.app --use-mock   # usa los JSON de ejemplo
```
Cuando cargue la consola:
- Enter: refresca los datos
- c: cambia distrito/estación/región
- q: salir

## Archivos útiles
- `app.py`: consola interactiva en memoria
- `collector.py`: descarga o lee los mocks
- `alerts.py`: compara dos snapshots y muestra cambios
- `config.py`: trae los valores por defecto ya hardcodeados
- `db.py`: solo guarda el último snapshot en memoria
