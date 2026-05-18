# Gestión de credenciales — Citas Médicas

## Por qué existe este setup
GitGuardian escanea cada commit en busca de contraseñas, tokens y claves hardcodeadas. Si detecta alguna, **bloquea el push automáticamente**. Las contraseñas de Oracle que estaban hardcodeadas en `settings.py` habrían sido bloqueadas.

---

## Archivos creados / modificados

| Archivo | Se sube a git | Propósito |
|---|---|---|
| `django_app/.env` | **NO** (en `.gitignore`) | Credenciales reales locales |
| `django_app/.env.example` | **SÍ** | Plantilla sin valores reales |
| `.gitignore` | **SÍ** | Excluye `.env` + nota GitGuardian |
| `gestion_citas/settings.py` | **SÍ** | Lee vars con `python-decouple` |

---

## Cómo arranca cada integrante del equipo

```bash
# 1. Clonar el repo (solo tiene .env.example, no .env)
git clone https://github.com/FrankDesarrollo/Gestion_citas_medicas

# 2. Crear el .env local a partir de la plantilla
cp django_app/.env.example django_app/.env

# 3. Editar .env con las credenciales reales (Frank las comparte por chat)
# Nunca por el repo.

# 4. Levantar en modo SQLite (sin Oracle)
cd django_app
$env:USE_SQLITE = "1"      # PowerShell
# export USE_SQLITE=1      # bash/zsh
py manage.py runserver
```

---

## Regla para el equipo

> **Nunca peguen una password en `settings.py`, `views.py`, ni en ningún `.py`.** Todo va en `.env`. Si GitGuardian bloquea tu push, revisa que no hayas dejado una credencial hardcodeada en el código.
