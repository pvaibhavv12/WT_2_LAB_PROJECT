import subprocess
from subprocess import PIPE
p = subprocess.Popen(['python', 'p2.py'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
out, err = p.communicate(input='1'.encode())
out = out.decode().strip()
print(out=="")
print(err.decode()=="")
print(err.decode())