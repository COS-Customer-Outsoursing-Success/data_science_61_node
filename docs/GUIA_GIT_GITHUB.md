# Guía: subir cambios a GitHub desde la terminal de VS Code

> Paso a paso genérico, con ejemplos tomados de este mismo repositorio (`data_science_61_node`, remoto `origin`, rama `main`).

## 0. Abrir la terminal correcta

`Ctrl + ñ` (o menú **Terminal → New Terminal**). VS Code la abre automáticamente en la carpeta del proyecto que tengas abierta — pero **igual valídalo** en el paso 1, nunca lo des por hecho.

## 1. Validar que estás en el repositorio correcto — *siempre primero*

```powershell
git remote -v
git branch -vv
```

Qué mirar en la salida:

```
origin  https://github.com/COS-Customer-Outsoursing-Success/data_science_61_node.git (fetch)
origin  https://github.com/COS-Customer-Outsoursing-Success/data_science_61_node.git (push)

  backup-pre-purge-20260731 09b66fbc ...
* main                      fcc113b0 [origin/main] ...
```

- **`git remote -v`**: la URL debe apuntar al repo que tú esperas. Si no aparece nada, no estás dentro de un repositorio git; si apunta a otro repo, estás en la carpeta equivocada.
- **`git branch -vv`**: el `*` marca la rama en la que estás parado. El texto entre `[...]` (ej. `[origin/main]`) es la rama remota que sigue — si dice `up to date` más adelante en `git status`, vas sincronizado.

Si algo no cuadra, **detente aquí** — `cd` a la carpeta correcta antes de seguir.

## 2. Ver el panorama completo — qué cambió

```powershell
git status
```

Te separa todo en 3 grupos:

| Grupo | Qué significa |
|---|---|
| `Changes to be committed` | Ya está en *staging*, se incluirá en el próximo commit |
| `Changes not staged for commit` | Modificado en disco, pero **aún no** se va a commitear |
| `Untracked files` | Archivos nuevos que git todavía no conoce |

Para ver el contenido exacto de lo que cambió (no solo el nombre del archivo):

```powershell
git diff          # cambios sin stagear
git diff --staged # cambios ya stageados
```

**Revisa siempre `git diff` antes de continuar** — es tu última oportunidad de detectar un archivo que no debería subir (credenciales, `.env`, algo que quedó a medias).

## 3. Elegir qué archivos subir (`git add`)

Evita `git add .` o `git add -A` a ciegas — agrega archivos puntuales y así controlas exactamente qué entra:

```powershell
git add docs/ARQUITECTURA_WHATSAPP.md docs/manual_uso.md
git add src/excel_app/_cls_excel_auto_manager.py
```

Si de verdad quieres agregar todo lo que aparece en `git status`, hazlo — pero corre `git status` inmediatamente después para confirmar qué quedó en *staging* antes de commitear.

## 4. Última revisión antes de comitear

```powershell
git status
git diff --staged
```

Si algo no debería estar ahí:

```powershell
git restore --staged <archivo>   # lo saca de staging, sin perder el cambio en disco
```

## 5. Crear el commit

```powershell
git commit -m "tipo: resumen corto de qué y por qué"
```

Convención simple: `fix:` para corrección de bug, `feat:` para algo nuevo, `docs:` para documentación, `chore:` para mantenimiento (revisa `git log --oneline -10` de este repo para ver el estilo que ya se usa aquí). El mensaje explica el **porqué**, no repite el diff.

Para un mensaje de varias líneas en PowerShell, usa un here-string:

```powershell
git commit -m @'
fix: corrige cierre indiscriminado de Excel

Antes cerraba todas las instancias de EXCEL.EXE de la maquina;
ahora solo cierra el libro de la campana que corresponde.
'@
```

## 6. Sincronizar antes de subir

Si alguien más pudo haber subido cambios mientras tú trabajabas:

```powershell
git pull
```

- Si dice `Already up to date`, no había nada nuevo, sigue al paso 7.
- Si trae cambios y los combina solo, perfecto, sigue al paso 7.
- Si marca **conflicto** (`CONFLICT`), git te va a señalar los archivos afectados con marcas `<<<<<<<` / `=======` / `>>>>>>>` dentro del archivo. Hay que editarlos a mano para dejar el contenido correcto, luego `git add <archivo>` y `git commit` para cerrar el merge. (Si nunca te ha pasado, mejor pide ayuda la primera vez en vez de adivinar.)

## 7. Subir los cambios (`push`)

```powershell
git push
```

Si es la primera vez que subes una rama nueva (no `main`), git te va a pedir que definas a qué rama remota apunta:

```powershell
git push -u origin nombre-de-la-rama
```

El `-u` (`--set-upstream`) hace que las próximas veces baste con `git push` a secas.

## 8. Verificar que quedó arriba

```powershell
git status
```

Debe decir `Your branch is up to date with 'origin/main'`. También puedes confirmar visualmente entrando a la URL del remoto (la que te mostró `git remote -v`) en el navegador y viendo el commit más reciente.

## 9. Errores comunes

| Mensaje / síntoma | Causa | Solución |
|---|---|---|
| `rejected ... (fetch first)` | El remoto tiene commits que tú no tienes localmente | `git pull`, resolver conflictos si aparecen, y volver a `git push` |
| `fatal: not a git repository` | Estás en una carpeta que no es (o no está dentro de) un repo git | `cd` a la carpeta correcta y repetir el paso 1 |
| `Authentication failed` / pide usuario y contraseña en un pop-up que nunca acepta | Git en Windows usa el *Credential Manager*; a veces queda un token vencido | Ejecutar `git credential-manager reject https://github.com` y volver a intentar el `push` (te pedirá iniciar sesión de nuevo) |
| `Permission denied` al hacer push | Tu usuario de GitHub no tiene permiso de escritura en ese repo | Confirmar con quien administra el repo que tengas acceso, o subir a tu propia rama/fork y abrir un Pull Request |
| Un `git push` rechazado y no quieres perder tu commit | — | **Nunca** uses `git push --force` sin estar seguro; primero `git pull` y resuelve normal |

## 10. Checklist rápido antes de cualquier push

- [ ] `git remote -v` apunta al repo correcto
- [ ] `git branch -vv` confirma que estás en la rama esperada
- [ ] `git status` / `git diff` revisado — nada raro, ningún `.env` o secreto
- [ ] Mensaje de commit explica el porqué del cambio
- [ ] `git pull` antes de subir si trabajas junto con alguien más
