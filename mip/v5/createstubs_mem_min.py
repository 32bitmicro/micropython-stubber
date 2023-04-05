r='micropython'
q='machine'
p='nodename'
o='{}/{}'
n='method'
m='function'
l='bool'
k='str'
j='float'
i='int'
h=NameError
g=sorted
f=NotImplementedError
a=',\n'
Z='_'
Y='dict'
X='list'
W='tuple'
V=open
U=IndexError
T=repr
S='-'
R='sysname'
Q='version'
P=True
O='v'
N='build'
M=KeyError
L=ImportError
I='.'
K=len
J=print
H=AttributeError
G=False
F=''
D=None
A='/'
C='release'
B=OSError
import gc as E,sys,uos as os
from ujson import dumps as b
try:from collections import OrderedDict
except L:from ucollections import OrderedDict
__version__='v1.12.2'
s=2
t=2
class Stubber:
	def __init__(C,path=D,firmware_id=D):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise f('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		C._report=[];C.info=_info();E.collect()
		if D:C._fwid=D.lower()
		else:C._fwid='{family}-{ver}-{port}'.format(**C.info).lower()
		C._start_free=E.mem_free()
		if path:
			if path.endswith(A):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',A)
		try:c(path+A)
		except B:J('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		G=item_instance;A=[];J=[]
		for I in dir(G):
			try:
				B=getattr(G,I)
				try:C=T(type(B)).split("'")[1]
				except U:C=F
				if C in{i,j,k,l,W,X,Y}:D=1
				elif C in{m,n}:D=2
				elif C in'class':D=3
				else:D=4
				A.append((I,T(B),T(type(B)),B,D))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(I,G,K))
		A=g([B for B in A if not B[0].startswith(Z)],key=lambda x:x[4]);E.collect();return A,J
	def add_modules(A,modules):A.modules=g(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(C,module_name):
		D=module_name
		if D in C.problematic:return G
		if D in C.excluded:return G
		H='{}/{}.py'.format(C.path,D.replace(I,A));E.collect();F=G
		try:F=C.create_module_stub(D,H)
		except B:return G
		E.collect();return F
	def create_module_stub(K,module_name,file_name=D):
		H=file_name;C=module_name
		if H is D:H=K.path+A+C.replace(I,Z)+'.py'
		if A in C:C=C.replace(A,I)
		N=D
		try:N=__import__(C,D,D,'*');J('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,H,E.mem_free()))
		except L:return G
		c(H)
		with V(H,'w')as O:Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,K._fwid,K.info,__version__);O.write(Q);O.write('from typing import Any\n\n');K.write_object_stub(O,N,C,F)
		K._report.append('{{"module": "{}", "file": "{}"}}'.format(C,H.replace('\\',A)))
		if C not in{'os','sys','logging','gc'}:
			try:del N
			except (B,M):pass
			try:del sys.modules[C]
			except M:pass
		E.collect();return P
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';R=in_class;Q=object_expr;P='Exception';H=fp;C=indent;E.collect()
		if Q in N.problematic:return
		S,O=N.get_obj_attributes(Q)
		if O:J(O)
		for (D,L,G,T,f) in S:
			if D in['classmethod','staticmethod','BaseException',P]:continue
			if G=="<class 'type'>"and K(C)<=t*4:
				U=F;V=D.endswith(P)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=P
				A='\n{}class {}({}):\n'.format(C,D,U)
				if V:A+=C+'    ...\n';H.write(A);return
				H.write(A);N.write_object_stub(H,T,'{0}.{1}'.format(obj_name,D),C+'    ',R+1);A=C+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=C+'        ...\n\n';H.write(A)
			elif n in G or m in G:
				Z=b;a=F
				if R>0:a='self, '
				if c in G or c in L:A='{}@classmethod\n'.format(C)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(C,D,Z)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(C,D,a,Z)
				A+=C+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=F
				if I in[k,i,j,l,'bytearray','bytes']:A=d.format(C,D,L,I)
				elif I in[Y,X,W]:e={Y:'{}',X:'[]',W:'()'};A=d.format(C,D,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(C,D,I,G,L)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(C+D+' # type: Any\n')
		del S;del O
		try:del D,L,G,T
		except (B,M,h):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,Z)
		return A
	def clean(C,path=D):
		if path is D:path=C.path
		J('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except (B,H):return
		for F in E:
			A=o.format(path,F)
			try:os.remove(A)
			except B:
				try:C.clean(A);os.rmdir(A)
				except B:pass
	def report(A,filename='modules.json'):
		J('Created stubs for {} modules on board {}\nPath: {}'.format(K(A._report),A._fwid,A.path));F=o.format(A.path,filename);E.collect()
		try:
			with V(F,'w')as C:
				A.write_json_header(C);D=P
				for H in A._report:A.write_json_node(C,H,D);D=G
				A.write_json_end(C)
			I=A._start_free-E.mem_free()
		except B:J('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(b({A:B.info})[1:-1]);f.write(a);f.write(b({'stubber':{Q:__version__},'stubtype':A})[1:-1]);f.write(a);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(a)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def c(path):
	C=E=0
	while C!=-1:
		C=path.find(A,E)
		if C!=-1:
			D=path[0]if C==0 else path[:C]
			try:H=os.stat(D)
			except B as F:
				if F.args[0]==s:
					try:os.mkdir(D)
					except B as G:J('failed to create folder {}'.format(D));raise G
		E=C+1
def _info():
	a='0.0.0';Z='port';Y='platform';X='name';P='mpy';J='unknown';E='family';B='ver';T=sys.implementation.name;V='stm32'if sys.platform.startswith('pyb')else sys.platform;A={X:T,C:a,Q:a,N:F,R:J,p:J,q:J,E:T,Y:V,Z:V,B:F}
	try:A[C]=I.join([str(A)for A in sys.implementation.version]);A[Q]=A[C];A[X]=sys.implementation.name;A[P]=sys.implementation.mpy
	except H:pass
	if sys.platform not in('unix','win32'):
		try:u(A)
		except (U,H,TypeError):pass
	try:from pycopy import const as G;A[E]='pycopy';del G
	except (L,M):pass
	try:from pycom import FAT as G;A[E]='pycom';del G
	except (L,M):pass
	if A[Y]=='esp32_LoBo':A[E]='loboris';A[Z]='esp32'
	elif A[R]=='ev3':
		A[E]='ev3-pybricks';A[C]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[C]='2.0.0'
		except L:pass
	if A[C]:A[B]=O+A[C].lstrip(O)
	if A[E]==r:
		if A[C]and A[C]>='1.10.0'and A[C].endswith('.0'):A[B]=A[C][:-2]
		else:A[B]=A[C]
		if A[N]!=F and K(A[N])<4:A[B]+=S+A[N]
	if A[B][0]!=O:A[B]=O+A[B]
	if P in A:
		b=int(A[P]);W=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][b>>10]
		if W:A['arch']=W
	return A
def u(info):
	E=' on ';A=info;B=os.uname();A[R]=B[0];A[p]=B[1];A[C]=B[2];A[q]=B[4]
	if E in B[3]:
		D=B[3].split(E)[0]
		if A[R]=='esp8266':F=D.split(S)[0]if S in D else D;A[Q]=A[C]=F.lstrip(O)
		try:A[N]=D.split(S)[1]
		except U:pass
def get_root():
	try:C=os.getcwd()
	except (B,H):C=I
	D=C
	for D in [C,'/sd','/flash',A,I]:
		try:E=os.stat(D);break
		except B:continue
	return D
def v(filename):
	try:os.stat(filename);return P
	except B:return G
def d():sys.exit(1)
def read_path():
	path=F
	if K(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:d()
	elif K(sys.argv)==2:d()
	return path
def e():
	try:A=bytes('abc',encoding='utf8');B=e.__module__;return G
	except (f,H):return P
def main():
	stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[r]
	for C in [F,A,'/lib/']:
		try:
			with V(C+'modulelist'+'.txt')as D:stubber.modules=[A.strip()for A in D.read().split('\n')if K(A.strip())and A.strip()[0]!='#'];break
		except B:pass
	E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or e():
	try:logging.basicConfig(level=logging.INFO)
	except h:pass
	if not v('no_auto_stubber.txt'):main()