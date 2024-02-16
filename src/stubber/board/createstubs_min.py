z='No report file'
y='Failed to create the report.'
x='{}/{}'
w='logging'
v='sys'
u='method'
t='function'
s='bool'
r='str'
q='float'
p='int'
o='stubber'
n=TypeError
m=Exception
l=KeyError
k=sorted
j=NotImplementedError
f='pycom'
e=',\n'
d='dict'
c='list'
b='tuple'
a='micropython'
Z=repr
Y=print
V='-preview'
U=True
T='-'
S='board'
R=len
Q=open
P=IndexError
O='family'
N=ImportError
M=dir
K='port'
J='.'
I=AttributeError
H=False
G='/'
E=OSError
D=None
C='version'
B=''
import gc as F,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except N:pass
try:from collections import OrderedDict as g
except N:from ucollections import OrderedDict as g
__version__='v1.17.2'
A0=2
A1=2
A5=['lib','/lib','/sd/lib','/flash/lib',J]
class L:
	INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=Y
	@staticmethod
	def getLogger(name):return L()
	@classmethod
	def basicConfig(A,level):A.level=level
	def info(A,msg):
		if A.level<=L.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=L.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=L.ERROR:A.prnt('ERROR :',msg)
A=L.getLogger(o)
L.basicConfig(level=L.INFO)
class Stubber:
	def __init__(B,path=D,firmware_id=D):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise j('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		B.info=_info();A.info('Port: {}'.format(B.info[K]));A.info('Board: {}'.format(B.info[S]));F.collect()
		if C:B._fwid=C.lower()
		elif B.info[O]==a:B._fwid='{family}-v{version}-{port}-{board}'.format(**B.info).rstrip(T)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=F.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',G)
		try:W(path+G)
		except E:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[];B._json_name=D;B._json_first=H
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for A in M(H):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=getattr(H,A)
				try:E=Z(type(D)).split("'")[1]
				except P:E=B
				if E in{p,q,r,s,b,c,d}:G=1
				elif E in{t,u}:G=2
				elif E in'class':G=3
				else:G=4
				C.append((A,Z(D),Z(type(D)),D,G))
			except I as J:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,J))
			except MemoryError as J:Y('MemoryError: {}'.format(J));sleep(1);reset()
		C=k([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return C,K
	def add_modules(A,modules):A.modules=k(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber {} on {}'.format(__version__,B._fwid));B.report_start();F.collect()
		for C in B.modules:B.create_one_stub(C)
		B.report_end();A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return H
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return H
		I='{}/{}.pyi'.format(C.path,B.replace(J,G));F.collect();D=H
		try:D=C.create_module_stub(B,I)
		except E:return H
		F.collect();return D
	def create_module_stub(K,module_name,file_name=D):
		I=file_name;C=module_name
		if I is D:L=C.replace(J,'_')+'.pyi';I=K.path+G+L
		else:L=I.split(G)[-1]
		if G in C:C=C.replace(G,J)
		M=D
		try:M=__import__(C,D,D,'*');P=F.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,L,P))
		except N:return H
		W(I)
		with Q(I,'w')as O:R=str(K.info).replace('OrderedDict(',B).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,K._fwid,R,__version__);O.write(S);O.write('from __future__ import annotations\nfrom typing import Any, Generator\nfrom _typeshed import Incomplete\n\n');K.write_object_stub(O,M,C,B)
		K.report_add(C,I)
		if C not in{'os',v,w,'gc'}:
			try:del M
			except(E,l):A.warning('could not del new_module')
		F.collect();return U
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		X='generator';W='{0}{1}: {3} = {2}\n';V='bound_method';U='Incomplete';N=in_class;M='Exception';L=object_expr;I=fp;D=indent;F.collect()
		if L in K.problematic:A.warning('SKIPPING problematic module:{}'.format(L));return
		Y,O=K.get_obj_attributes(L)
		if O:A.error(O)
		for(E,J,H,Z,e)in Y:
			if E in['classmethod','staticmethod','BaseException',M]:continue
			if E[0].isdigit():A.warning('NameError: invalid name {}'.format(E));continue
			if H=="<class 'type'>"and R(D)<=A1*4:
				P=B;Q=E.endswith(M)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if Q:P=M
				C='\n{}class {}({}):\n'.format(D,E,P)
				if Q:C+=D+'    ...\n';I.write(C);continue
				I.write(C);K.write_object_stub(I,Z,'{0}.{1}'.format(obj_name,E),D+'    ',N+1);C=D+'    def __init__(self, *argv, **kwargs) -> None:\n';C+=D+'        ...\n\n';I.write(C)
			elif any(A in H for A in[u,t,'closure']):
				S=U;T=B
				if N>0:T='self, '
				if V in H or V in J:C='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,S)
				else:C='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,T,S)
				C+=D+'    ...\n\n';I.write(C)
			elif H=="<class 'module'>":0
			elif H.startswith("<class '"):
				G=H[8:-2];C=B
				if G in(r,p,q,s,'bytearray','bytes'):C=W.format(D,E,J,G)
				elif G in(d,c,b):a={d:'{}',c:'[]',b:'()'};C=W.format(D,E,a[G],G)
				elif G in('object','set','frozenset','Pin',X):
					if G==X:G='Generator'
					C='{0}{1}: {2} ## = {4}\n'.format(D,E,G,H,J)
				else:G=U;C='{0}{1}: {2} ## {3} = {4}\n'.format(D,E,G,H,J)
				I.write(C)
			else:I.write("# all other, type = '{0}'\n".format(H));I.write(D+E+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(C,path=D):
		if path is D:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);F=os.listdir(path)
		except(E,I):return
		for G in F:
			B=x.format(path,G)
			try:os.remove(B)
			except E:
				try:C.clean(B);os.rmdir(B)
				except E:pass
	def report_start(B,filename='modules.json'):
		H='firmware';B._json_name=x.format(B.path,filename);B._json_first=U;W(B._json_name);A.info('Report file: {}'.format(B._json_name));F.collect()
		try:
			with Q(B._json_name,'w')as G:G.write('{');G.write(dumps({H:B.info})[1:-1]);G.write(e);G.write(dumps({o:{C:__version__},'stubtype':H})[1:-1]);G.write(e);G.write('"modules" :[\n')
		except E as I:A.error(y);B._json_name=D;raise I
	def report_add(B,module_name,stub_file):
		if not B._json_name:raise m(z)
		try:
			with Q(B._json_name,'a')as C:
				if not B._json_first:C.write(e)
				else:B._json_first=H
				D='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',G));C.write(D)
		except E:A.error(y)
	def report_end(B):
		if not B._json_name:raise m(z)
		with Q(B._json_name,'a')as C:C.write('\n]}')
		A.info('Path: {}'.format(B.path))
def W(path):
	B=D=0
	while B!=-1:
		B=path.find(G,D)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except E as F:
				if F.args[0]==A0:
					try:os.mkdir(C)
					except E as H:A.error('failed to create folder {}'.format(C));raise H
		D=B+1
def X(s):
	C=' on '
	if not s:return B
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not T in s:return B
		A=s.split(T)[1];return A
	if not V in s:return B
	A=s.split(V)[1].split(J)[1];return A
def _info():
	Y='ev3-pybricks';W='pycopy';U='unix';T='win32';R='arch';Q='cpu';L='ver';F='mpy';E='build';A=g({O:sys.implementation.name,C:B,E:B,L:B,K:sys.platform,S:'UNKNOWN',Q:B,F:B,R:B})
	if A[K].startswith('pyb'):A[K]='stm32'
	elif A[K]==T:A[K]='windows'
	elif A[K]=='linux':A[K]=U
	try:A[C]=A2(sys.implementation.version)
	except I:pass
	try:H=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[S]=H;A[Q]=H.split('with')[-1].strip();A[F]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if F in M(sys.implementation)else B
	except(I,P):pass
	A[S]=A3()
	try:
		if'uname'in M(os):
			A[E]=X(os.uname()[3])
			if not A[E]:A[E]=X(os.uname()[2])
		elif C in M(sys):A[E]=X(sys.version)
	except(I,P,n):pass
	if A[C]==B and sys.platform not in(U,T):
		try:Z=os.uname();A[C]=Z.release
		except(P,I,n):pass
	for(b,c,d)in[(W,W,'const'),(f,f,'FAT'),(Y,'pybricks.hubs','EV3Brick')]:
		try:e=__import__(c,D,D,d);A[O]=b;del e;break
		except(N,l):pass
	if A[O]==Y:A['release']='2.0.0'
	if A[O]==a:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if F in A and A[F]:
		G=int(A[F]);J=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][G>>10]
		if J:A[R]=J
		A[F]='v{}.{}'.format(G&255,G>>8&3)
	if A[E]and not A[C].endswith(V):A[C]=A[C]+V
	A[L]=f"{A[C]}-{A[E]}"if A[E]else f"{A[C]}";return A
def A2(version):
	A=version;B=J.join([str(A)for A in A[:3]])
	if R(A)>3 and A[3]:B+=T+A[3]
	return B
def A3():
	try:from boardname import BOARDNAME as C;A.info('Found BOARDNAME: {}'.format(C))
	except N:A.warning('BOARDNAME not found');C=B
	return C
def get_root():
	try:A=os.getcwd()
	except(E,I):A=J
	B=A
	for B in[A,'/sd','/flash',G,J]:
		try:C=os.stat(B);break
		except E:continue
	return B
def A4(filename):
	try:
		if os.stat(filename)[0]>>14:return U
		return H
	except E:return H
def h():Y("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if R(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:h()
	elif R(sys.argv)==2:h()
	return path
def i():
	try:A=bytes('abc',encoding='utf8');B=i.__module__;return H
	except(j,I):return U
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_asyncio','_boot_fat','_coap','_espnow','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','cmath','collections','crypto','cryptolib','curl','deflate','dht','display','display_driver_utils','ds18x20','encoder','errno','esp','esp32','espidf','espnow','ffi','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','json','lcd160cr','lodepng',w,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','math','microWebSocket','microWebSrv','microWebTemplate',a,'mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pcf85063a','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform','pyb',f,'pye','qrcode','queue','random','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','struct',v,'termios','time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',C,'websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];F.collect();stubber.create_all_stubs()
if __name__=='__main__'or i():
	if not A4('no_auto_stubber.txt'):
		try:F.threshold(4*1024);F.enable()
		except BaseException:pass
		main()