"""One-time isolated laptop dependency setup, then native app. No robot access."""
import os
from pathlib import Path
import subprocess
import sys
import venv


def main():
    directory=Path(__file__).resolve().parent
    if '--demo' in sys.argv:
        return subprocess.call([sys.executable,str(directory/'hub.py'),'--demo'])
    runtime=Path(os.environ.get('LOCALAPPDATA',str(Path.home()))) / 'FahadRobotHub' / 'runtime'
    python=runtime / 'Scripts' / 'python.exe'
    pythonw=runtime / 'Scripts' / 'pythonw.exe'
    if not python.exists():
        print('First-time laptop setup: creating a private Python environment. Robot software is unchanged.',flush=True)
        venv.EnvBuilder(with_pip=True).create(str(runtime))
    marker=runtime / 'hub-dependencies-5.1.0.ok'
    if not marker.exists():
        print('Installing the laptop SSH library. Laptop internet is needed for this first setup only.',flush=True)
        result=subprocess.call([str(python),'-m','pip','install','--only-binary=:all:','--disable-pip-version-check','-r',str(directory/'requirements.txt')])
        if result:
            print('Setup failed. No robot connection was attempted. Restore laptop internet and run Start Robot Hub.cmd again.')
            return result
        marker.write_text('paramiko==5.1.0\n',encoding='ascii')
    subprocess.Popen([str(pythonw if pythonw.exists() else python),str(directory/'hub.py')],
                     creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),cwd=str(directory))
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:
        print('Laptop hub setup could not finish: '+str(exc))
        sys.exit(1)
