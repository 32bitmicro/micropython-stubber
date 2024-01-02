x='with'
w='pyb'
v='stubber'
u='{}/{}'
t='logging'
s='sys'
r='method'
q='function'
p='bool'
o='str'
n='float'
m='int'
l=NameError
k=sorted
j=NotImplementedError
c='pycom'
b=',\n'
a='dict'
Z='list'
Y='tuple'
X='micropython'
W=open
V=repr
T='cpu'
S='_'
R=len
Q=KeyError
P=IndexError
O=dir
N=print
M=ImportError
L='family'
K=True
J='.'
I=AttributeError
H='board'
A=False
G='/'
E=None
F=OSError
D='version'
B=''
import gc as C,os,sys
from ujson import dumps as d
try:from machine import reset
except M:pass
try:from collections import OrderedDict as e
except M:from ucollections import OrderedDict as e
__version__='v1.16.2'
y=2
z=2
A0=[J,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise j('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();C.collect()
		if B:A._fwid=B.lower()
		elif A.info[L]==X:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:f(path+G)
		except F:N('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;D=[];J=[]
		for A in O(H):
			if A.startswith(S)and not A in L.modules:continue
			try:
				E=getattr(H,A)
				try:F=V(type(E)).split("'")[1]
				except P:F=B
				if F in{m,n,o,p,Y,Z,a}:G=1
				elif F in{q,r}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,V(E),V(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,K))
			except MemoryError as K:sleep(1);reset()
		D=k([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);C.collect();return D,J
	def add_modules(A,modules):A.modules=k(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(B,module_name):
		D=module_name
		if D in B.problematic:return A
		if D in B.excluded:return A
		H='{}/{}.py'.format(B.path,D.replace(J,G));C.collect();E=A
		try:E=B.create_module_stub(D,H)
		except F:return A
		C.collect();return E
	def create_module_stub(I,module_name,file_name=E):
		H=file_name;D=module_name
		if H is E:O=D.replace(J,S)+'.py';H=I.path+G+O
		else:O=H.split(G)[-1]
		if G in D:D=D.replace(G,J)
		L=E
		try:L=__import__(D,E,E,'*');T=C.mem_free()
		except M:return A
		f(H)
		with W(H,'w')as N:P=str(I.info).replace('OrderedDict(',B).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,I._fwid,P,__version__);N.write(R);N.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(N,L,D,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os',s,t,'gc'}:
			try:del L
			except(F,Q):pass
			try:del sys.modules[D]
			except Q:pass
		C.collect();return K
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Incomplete';P=in_class;O=object_expr;M='Exception';H=fp;D=indent;C.collect()
		if O in K.problematic:return
		S,L=K.get_obj_attributes(O)
		if L:N(L)
		for(E,J,G,T,f)in S:
			if E in['classmethod','staticmethod','BaseException',M]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and R(D)<=z*4:
				U=B;V=E.endswith(M)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=M
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),D+'    ',P+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif any(A in G for A in[r,q,'closure']):
				W=b;X=B
				if P>0:X='self, '
				if c in G or c in J:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,X,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[o,m,n,p,'bytearray','bytes']:A=d.format(D,E,J,I)
				elif I in[a,Z,Y]:e={a:'{}',Z:'[]',Y:'()'};A=d.format(D,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,I,G,J)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+E+' # type: Incomplete\n')
		del S;del L
		try:del E,J,G,T
		except(F,Q,l):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,S)
		return A
	def clean(B,path=E):
		if path is E:path=B.path
		try:os.stat(path);C=os.listdir(path)
		except(F,I):return
		for D in C:
			A=u.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(B,filename='modules.json'):
		G=u.format(B.path,filename);C.collect()
		try:
			with W(G,'w')as D:
				B.write_json_header(D);E=K
				for H in B._report:B.write_json_node(D,H,E);E=A
				B.write_json_end(D)
			I=B._start_free-C.mem_free()
		except F:N('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(d({A:B.info})[1:-1]);f.write(b);f.write(d({v:{D:__version__},'stubtype':A})[1:-1]);f.write(b);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(b)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def f(path):
	A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except F as D:
				if D.args[0]==y:
					try:os.mkdir(B)
					except F as E:N('failed to create folder {}'.format(B));raise E
		C=A+1
def U(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	d='ev3-pybricks';b='pycopy';a='unix';Z='win32';Y='arch';W='ver';K='mpy';G='port';F='build';A=e({L:sys.implementation.name,D:B,F:B,W:B,G:sys.platform,H:'UNKNOWN',T:B,K:B,Y:B})
	if A[G].startswith(w):A[G]='stm32'
	elif A[G]==Z:A[G]='windows'
	elif A[G]=='linux':A[G]=a
	try:A[D]=J.join([str(A)for A in sys.implementation.version]).rstrip(J)
	except I:pass
	try:S=sys.implementation._machine if'_machine'in O(sys.implementation)else os.uname().machine;A[H]=S;A[T]=S.split(x)[-1].strip();A[K]=sys.implementation._mpy if'_mpy'in O(sys.implementation)else sys.implementation.mpy if K in O(sys.implementation)else B
	except(I,P):pass
	C.collect();A1(A);C.collect()
	try:
		A[F]=U(os.uname()[3])
		if not A[F]:A[F]=U(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=U(sys.version.split(';')[1])
	except(I,P):pass
	if A[F]and R(A[F])>5:A[F]=B
	if A[D]==B and sys.platform not in(a,Z):
		try:f=os.uname();A[D]=f.release
		except(P,I,TypeError):pass
	for(g,h,i)in[(b,b,'const'),(c,c,'FAT'),(d,'pybricks.hubs','EV3Brick')]:
		try:j=__import__(h,E,E,i);A[L]=g;del j;break
		except(M,Q):pass
	if A[L]==d:A['release']='2.0.0'
	if A[L]==X:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if K in A and A[K]:
		N=int(A[K]);V=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][N>>10]
		if V:A[Y]=V
		A[K]='v{}.{}'.format(N&255,N>>8&3)
	A[W]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def A1(info,desc=B):
	L='with ';D=info;F=A
	for G in[A+'/board_info.csv'for A in A0]:
		if g(G):
			E=desc or D[H].strip();I=E.rfind(' with')
			if I!=-1:J=E[:I].strip()
			else:J=B
			if A2(D,E,G,J):F=K;break
	if not F:
		E=desc or D[H].strip()
		if L+D[T].upper()in E:E=E.split(L+D[T].upper())[0].strip()
		D[H]=E
	D[H]=D[H].replace(' ',S);C.collect()
def A2(info,descr,filename,short_descr):
	D=short_descr;C=info;E=B
	with W(filename,'r')as J:
		while 1:
			F=J.readline()
			if not F:break
			I,G=F.split(',')[0].strip(),F.split(',')[1].strip()
			if I==descr:C[H]=G;return K
			elif D and I==D:
				if x in D:C[H]=G;return K
				E=G
	if E:C[H]=E;return K
	return A
def get_root():
	try:A=os.getcwd()
	except(F,I):A=J
	B=A
	for B in[A,'/sd','/flash',G,J]:
		try:C=os.stat(B);break
		except F:continue
	return B
def g(filename):
	try:
		if os.stat(filename)[0]>>14:return K
		return A
	except F:return A
def h():sys.exit(1)
def read_path():
	path=B
	if R(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:h()
	elif R(sys.argv)==2:h()
	return path
def i():
	try:B=bytes('abc',encoding='utf8');C=i.__module__;return A
	except(j,I):return K
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_asyncio','_boot_fat','_coap','_espnow','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','cmath','collections','crypto','cryptolib','curl','deflate','dht','display','display_driver_utils','ds18x20','encoder','errno','esp','esp32','espidf','espnow','ffi','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','json','lcd160cr','lodepng',t,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','math','microWebSocket','microWebSrv','microWebTemplate',X,'mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pcf85063a','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform',w,c,'pye','qrcode','queue','random','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','struct',s,'termios','time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',D,'websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or i():
	try:A3=logging.getLogger(v);logging.basicConfig(level=logging.INFO)
	except l:pass
	if not g('no_auto_stubber.txt'):
		try:C.threshold(4*1024);C.enable()
		except BaseException:pass
		main()