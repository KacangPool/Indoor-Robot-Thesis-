"""Fahad Robot Hub: native Windows setup/status app, no movement publisher."""
import argparse
import copy
import json
from pathlib import Path
import queue
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

from agent import VERSION
from connection import RobotConnection, HubController

SOURCE = Path(__file__).resolve().parent.parent / 'remote_dashboard'
BG, PANEL, LINE, TEXT, MUTED = '#0b1218', '#14212b', '#2a3b49', '#e7eff5', '#9eb2c3'
MINT, AMBER, RED = '#8ad8bd', '#efc378', '#ffb6bf'


class DemoConnection:
    """Explicit disconnected UI/test mode. Never opens SSH, browser or a port."""
    def __init__(self, host='192.168.0.100'):
        self.host = host
        self.manifest = None
        self.services = {name: 'stopped' for name in ('camera','lidar','base','dashboard')}
        self.dashboard = None
    def connect(self, password): pass
    def install_agent(self): pass
    def install_runtime(self, source, manifest): self.manifest = manifest;return {'verified':True}
    def rpc(self, action, value=None):
        if action == 'start':
            old = self.services[value]
            self.services[value] = 'ready'
            if value == 'dashboard':
                self.dashboard = {'version':VERSION,'boot_id':'DEMO_NO_ROBOT','motor_output':False,
                    'control':{'armed':False,'ready':True,'stage':'disabled','joystick_speed_request_m_s':.10},
                    'cameras':{'rgb':{'available':True,'frame_id':'DEMO'},'yolo':{'available':True}},
                    'scan':{'available':True,'state':'live','arrival_rate_hz':10,'frame':'DEMO'}}
            return {'action':'reused' if old == 'ready' else 'started'}
        if action == 'logs': return {'text':'DEMO ONLY: no real service or log file. No robot connection.'}
        if action == 'stop-drive': return {'armed':False}
        if action == 'status':
            return copy.deepcopy({'agent_version':VERSION,'services':self.services,'graph':{'reachable':self.services['camera']=='ready','nodes':['DEMO_ONLY']},
                'dashboard':self.dashboard,'runtime_ok':bool(self.manifest),
                'installed_bundle':self.manifest['bundle_id'] if self.manifest else None,'owned':{},'device_lidar':False})
        raise RuntimeError('Unsupported demo action')
    def ensure_tunnel(self, boot): return 'DEMO_NO_ROBOT'
    def close(self): pass


class App:
    def __init__(self, root, demo=False):
        self.root, self.demo = root, demo
        self.events = queue.Queue()
        self.cancelled = threading.Event()
        self.controller = None
        self.connection = None
        self.last = None
        self.busy = False
        self.closing = False
        self.task_started = None
        self.task_phase = 'Idle'
        self.show_progress = False
        self.task_generation = 0
        self.host = tk.StringVar(value='192.168.0.100')
        self.password = tk.StringVar()
        self.ack = tk.BooleanVar(value=demo)
        self.banner = tk.StringVar(value='DEMO · NO ROBOT' if demo else 'DISCONNECTED')
        self.note = tk.StringVar(value='Connect once. Check, prepare and open your robot workspace from here.')
        self.root.title('Fahad · Robot Hub' + (' — DEMO / NO ROBOT' if demo else ''))
        self.root.geometry('1120x730')
        self.root.minsize(1000,650)
        self.root.configure(bg=BG)
        self._build()
        root.protocol('WM_DELETE_WINDOW',self.close)
        root.after(80,self._drain)
        root.after(4000,self._monitor)

    def label(self,parent,text,fg=TEXT,size=11,bold=False,**kwargs):
        return tk.Label(parent,text=text,bg=parent['bg'],fg=fg,font=('Segoe UI',size,'bold' if bold else 'normal'),**kwargs)

    def button(self,parent,text,command,primary=False,stop=False):
        return tk.Button(parent,text=text,command=command,bg=RED if stop else MINT if primary else '#213441',
            fg='#112b22' if primary else '#32151c' if stop else TEXT,activebackground='#afdccb',
            relief='flat',borderwidth=0,padx=16,pady=10,font=('Segoe UI',10,'bold'),cursor='hand2')

    def _build(self):
        style=ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TNotebook',background=BG,borderwidth=0)
        style.configure('TNotebook.Tab',background=PANEL,foreground=MUTED,padding=(12,6))
        style.map('TNotebook.Tab',background=[('selected','#213441')],foreground=[('selected',MINT)])
        header=tk.Frame(self.root,bg=BG);header.pack(fill='x',padx=28,pady=(14,10))
        logo=self.label(header,'F',fg=BG,size=24,bold=True,padx=15,pady=5);logo.configure(bg=MINT);logo.pack(side='left')
        names=tk.Frame(header,bg=BG);names.pack(side='left',padx=14)
        self.label(names,'FAHAD / ROBOT HUB',size=18,bold=True).pack(anchor='w')
        self.label(names,'ONE CONNECTION · SENSORS · CONTROLS · DIAGNOSTICS',fg=MUTED,size=9).pack(anchor='w',pady=(4,0))
        self.label(header,'DASHBOARD v'+VERSION,fg=MUTED,size=9).pack(side='right')
        self.state_label=tk.Label(header,textvariable=self.banner,bg=BG,fg=AMBER,font=('Segoe UI',10,'bold'))
        self.state_label.pack(side='right',padx=20)
        connection=tk.Frame(self.root,bg=PANEL,highlightbackground=LINE,highlightthickness=1);connection.pack(fill='x',padx=28)
        row=tk.Frame(connection,bg=PANEL);row.pack(fill='x',padx=18,pady=(15,10))
        self.label(row,'ROBOT',fg=MUTED,size=9,bold=True).pack(side='left',padx=(0,9))
        tk.Entry(row,textvariable=self.host,width=17,bg=BG,fg=TEXT,insertbackground=TEXT,relief='flat',font=('Consolas',11)).pack(side='left',ipady=7)
        self.label(row,'wheeltec',fg=MUTED,size=10).pack(side='left',padx=12)
        self.label(row,'PASSWORD',fg=MUTED,size=9,bold=True).pack(side='left',padx=(8,9))
        self.password_entry=tk.Entry(row,textvariable=self.password,show='●',width=19,bg=BG,fg=TEXT,insertbackground=TEXT,relief='flat')
        self.password_entry.pack(side='left',ipady=8)
        if self.demo:self.password_entry.configure(state='disabled')
        self.connect_button=self.button(row,'Connect & prepare',lambda:self.connect(True),primary=True);self.connect_button.pack(side='right')
        self.check_button=self.button(row,'Connect / reconnect',lambda:self.connect(False));self.check_button.pack(side='right',padx=9)
        tk.Checkbutton(connection,text='Robot stationary and directly in sight; wheels clear, normal physical power-off reachable.',variable=self.ack,
            bg=PANEL,fg=MUTED,selectcolor=BG,activebackground=PANEL,activeforeground=TEXT,font=('Segoe UI',10),anchor='w').pack(fill='x',padx=16,pady=(0,12))
        self.notice=tk.Label(self.root,textvariable=self.note,bg=BG,fg=AMBER,anchor='w',justify='left',wraplength=1030,font=('Segoe UI',10))
        self.notice.pack(fill='x',padx=28,pady=(12,10))
        progress_row=tk.Frame(self.root,bg=BG);progress_row.pack(fill='x',padx=28,pady=(0,6))
        self.progress=ttk.Progressbar(progress_row,mode='indeterminate',length=180)
        self.progress.pack(side='left')
        self.progress_text=self.label(progress_row,'Idle · no setup task running',fg=MUTED,size=9)
        self.progress_text.pack(side='left',padx=12)
        self.cards={}
        grid=tk.Frame(self.root,bg=BG);grid.pack(fill='x',padx=22)
        for index,(name,title) in enumerate((('ssh','SSH / TUNNEL'),('ros','ROS MASTER'),('camera','CAMERA + YOLO'),('lidar','2D LIDAR'),('base','ISOLATED BASE'),('dashboard','WEB WORKSPACE'))):
            card=tk.Frame(grid,bg=PANEL,highlightbackground=LINE,highlightthickness=1);card.grid(row=index//3,column=index%3,sticky='nsew',padx=6,pady=6)
            grid.columnconfigure(index%3,weight=1,uniform='cards')
            self.label(card,title,fg=MUTED,size=9,bold=True).pack(anchor='w',padx=15,pady=(9,4))
            value=self.label(card,'NOT CHECKED',fg=AMBER,size=16,bold=True);value.pack(anchor='w',padx=15)
            detail=self.label(card,'No connection claimed',fg=MUTED,size=9,anchor='w',justify='left',wraplength=300)
            detail.pack(fill='x',padx=15,pady=(4,9));self.cards[name]=(value,detail)
        actions=tk.Frame(self.root,bg=BG);actions.pack(fill='x',padx=28,pady=14)
        self.button(actions,'Colour camera',lambda:self.open_view('rgb')).pack(side='left')
        self.button(actions,'YOLO detections',lambda:self.open_view('yolo')).pack(side='left',padx=8)
        self.button(actions,'Driving + LiDAR',lambda:self.open_view(None),primary=True).pack(side='left')
        self.button(actions,'Stop driving',self.stop_drive,stop=True).pack(side='right')
        self.button(actions,'Check now',self.check).pack(side='right',padx=8)
        tabs=ttk.Notebook(self.root);tabs.pack(fill='both',expand=True,padx=28,pady=(0,12))
        logs=tk.Frame(tabs,bg=PANEL);tabs.add(logs,text='Activity & service logs')
        tools=tk.Frame(logs,bg=PANEL);tools.pack(fill='x',padx=10,pady=8)
        for name in ('camera','lidar','base','dashboard'):
            self.button(tools,name.title()+' log',lambda n=name:self.service_log(n)).pack(side='left',padx=3)
        self.button(tools,'Save report',self.save_report).pack(side='right')
        self.output=tk.Text(logs,bg='#0b171e',fg='#bfd3df',font=('Consolas',10),relief='flat',height=7,wrap='word',state='disabled')
        self.output.pack(fill='both',expand=True,padx=12,pady=(0,12))
        help_frame=tk.Frame(tabs,bg=PANEL);tabs.add(help_frame,text='How this works')
        help_text=('Join the robot network first; this app does not change Wi-Fi or USB tethering.\n\n'
            'Enter the robot password once per connection. It is cleared from the field and not saved. Saved SSH host identities are verified, never silently replaced.\n\n'
            'Prepare checks/reuses ROS nodes, installs the personal dashboard update when safe, starts missing services and creates the loopback tunnel. It never enables or sends movement.\n\n'
            'Camera and driving open the existing website in your browser. Camera exposure/gain settings are not implemented here; manual tilt remains physical.\n\n'
            'The website remains available. Phone access still needs its own trusted connection; phone localhost is not the laptop tunnel. Nothing is exposed publicly.\n\n'
            'Closing the hub attempts software Stop and disconnects. Remote sensor/base processes remain running. This is not Ubuntu shutdown or a physical emergency stop.\n\n'
            'Reused services may still depend on their old terminal. After a normal fresh robot boot, services started by the hub use detached processes and personal logs. No boot auto-start is configured.')
        self.label(help_frame,help_text,fg=MUTED,size=10,justify='left',anchor='nw',wraplength=1000).pack(fill='both',padx=20,pady=20)
        footer=tk.Frame(self.root,bg=BG);footer.pack(side='bottom',before=tabs,fill='x',padx=28,pady=(0,10))
        self.label(footer,'RESEARCH PROTOTYPE · software Stop is not a physical emergency stop',fg=MUTED,size=9).pack(side='left')
        self.button(footer,'Disconnect & close',self.close).pack(side='right',padx=(8,0))
        self.button(footer,'Cancel setup',self.cancel_setup).pack(side='right')
        if self.demo:self.log('DEMO ONLY. No SSH, ROS, serial access, uploads, tunnel or real browser connection.')

    def log(self,text):self.events.put(('log',text))

    def run(self,fn,label='Working',show_progress=True):
        if self.busy or self.closing:return
        self.busy=True;self.cancelled.clear();self._buttons()
        self.task_started=time.monotonic();self.task_phase=label;self.show_progress=show_progress
        self.task_generation+=1
        if show_progress:self.progress.start(12);self._progress_tick(self.task_generation)
        def work():
            try:
                result=fn()
                if isinstance(result,dict) and 'services' in result:self.events.put(('status',result))
            except Exception as exc:self.events.put(('error',str(exc)))
            finally:self.events.put(('done',None))
        threading.Thread(target=work,daemon=True).start()

    def _progress_tick(self,generation):
        if self.closing or not self.busy or not self.show_progress or generation!=self.task_generation:return
        elapsed=int(time.monotonic()-self.task_started)
        self.progress_text.configure(text=self.task_phase+' · '+str(elapsed)+' s')
        self.root.after(250,lambda:self._progress_tick(generation))

    def cancel_setup(self):
        self.cancelled.set()
        self.task_phase='Cancellation requested; waiting for current bounded step'
        self.note.set('Cancel requested. Already-started services remain; cancellation is not a physical stop.')

    def _buttons(self):
        for button in (self.connect_button,self.check_button):button.configure(state='disabled' if self.busy else 'normal')

    def connect(self,prepare):
        if prepare and not self.ack.get():
            self.note.set('Acknowledge stationary setup before starting/updating services. Check-only remains available.');return
        password=self.password.get();self.password.set('')
        host=self.host.get().strip()
        def work():
            if not prepare and self.connection:
                try:self.connection.rpc('stop-drive')
                except Exception:pass
                self.connection.close();self.connection=None;self.controller=None
            if self.connection is None:
                self.events.put(('phase','Connecting to robot over SSH'))
                connection=DemoConnection(host) if self.demo else RobotConnection(host)
                connection.connect(password)
                if self.closing or self.cancelled.is_set():connection.close();return
                try:
                    self.events.put(('phase','Installing personal connection helper'))
                    connection.install_agent()
                    controller=HubController(connection,SOURCE,self.log,self.cancelled,lambda status:self.events.put(('status',status)),lambda phase:self.events.put(('phase',phase)))
                except Exception:
                    connection.close();raise
                self.connection=connection;self.controller=controller
                self.log('Connected. Personal helper installed; password is not written to files.')
            return self.controller.prepare() if prepare else self.controller.check()
        self.run(work,'Connecting and preparing' if prepare else 'Connecting and checking')

    def check(self):
        if self.controller:self.run(self.controller.check,'Checking robot status')
        else:self.note.set('Connect first. Check-only does not start ROS services.')

    def _render(self,status):
        self.last=status
        self.banner.set('DEMO · NO ROBOT' if self.demo else 'SSH CONNECTED')
        self.cards['ssh'][0].configure(text='SIMULATED' if self.demo else 'CONNECTED',fg=AMBER if self.demo else MINT)
        self.cards['ssh'][1].configure(text='No real connection' if self.demo else 'Verified SSH · loopback tunnel' if self.controller and self.controller.url else 'Verified SSH · tunnel not prepared yet')
        reachable=status.get('graph',{}).get('reachable',False)
        self.cards['ros'][0].configure(text='SIMULATED' if self.demo else 'REACHABLE' if reachable else 'UNAVAILABLE',fg=AMBER if self.demo or not reachable else MINT)
        self.cards['ros'][1].configure(text=str(len(status.get('graph',{}).get('nodes',[])))+' registered nodes · not a freshness guarantee')
        dash=status.get('dashboard') or {}
        for name in ('camera','lidar','base','dashboard'):
            phase=status['services'][name]
            label=phase.upper()
            if phase=='ready':
                if name=='camera' and not dash.get('cameras',{}).get('rgb',{}).get('available'):label='WAITING FOR IMAGE'
                if name=='lidar' and not dash.get('scan',{}).get('available'):label='WAITING FOR SCAN'
                if name=='base' and not dash.get('control',{}).get('ready') and dash.get('control',{}).get('stage')!='holding':label='REGISTERED'
                if name=='dashboard' and dash.get('version')!=VERSION:label='VERSION MISMATCH'
            self.cards[name][0].configure(text='SIMULATED' if self.demo else label,fg=AMBER if self.demo or label!='READY' else MINT)
            ownership='hub-managed' if status.get('owned',{}).get(name,{}).get('alive') else 'existing/external' if phase=='ready' else 'not started'
            detail=ownership
            if name=='camera':detail+=' · RGB '+('recent' if dash.get('cameras',{}).get('rgb',{}).get('available') else 'not yet verified')
            if name=='lidar':detail+=' · '+dash.get('scan',{}).get('state','scan data not yet verified')
            if name=='base':detail+=' · '+dash.get('control',{}).get('stage','odometry readiness not yet verified')
            if name=='dashboard':
                speed=dash.get('control',{}).get('joystick_speed_request_m_s')
                detail='Running v'+str(dash.get('version','—'))+' · joystick '+(str(speed)+' m/s request' if speed is not None else 'limit unverified')
                detail+=' · source v'+VERSION
            self.cards[name][1].configure(text=detail)
        control=dash.get('control',{})
        event=control.get('last_disable')
        if event and event!=getattr(self,'last_disable_event',None):
            self.last_disable_event=event
            self.log('LAST BACKEND DISABLE: '+str(event.get('reason','Unknown')))
        if self.demo:self.note.set('DEMO ONLY: simulated cards, no robot connected and no real commands.')
        elif dash and dash.get('version')!=VERSION:self.note.set('Version mismatch: robot v'+str(dash.get('version'))+', local v'+VERSION+'. Release and Stop before Prepare installs the update.')
        elif control.get('readiness'):self.note.set('Services checked. Driving readiness: '+str(control['readiness']))
        else:self.note.set('Services checked. Startup never requests motion. Use the browser controls while watching the robot directly.')

    def _drain(self):
        if self.closing:return
        try:
            while True:
                kind,value=self.events.get_nowait()
                if kind=='log':
                    self.output.configure(state='normal');self.output.insert('end',value+'\n')
                    if int(self.output.index('end-1c').split('.')[0])>700:self.output.delete('1.0','200.0')
                    self.output.see('end');self.output.configure(state='disabled')
                elif kind=='status':self._render(value)
                elif kind=='error':self.note.set(value);self.log('CHECK REQUIRED: '+value);self.banner.set('CHECK REQUIRED')
                elif kind=='phase':self.task_phase=value
                elif kind=='done':
                    self.busy=False;self.progress.stop();self.progress.configure(value=0)
                    if self.show_progress:self.progress_text.configure(text='Task finished · see status and activity log')
                    self.show_progress=False;self._buttons()
        except queue.Empty:pass
        self.root.after(80,self._drain)

    def _monitor(self):
        if self.closing:return
        if self.controller and not self.busy:self.run(self.controller.check,show_progress=False)
        self.root.after(4000,self._monitor)

    def open_view(self,view):
        if self.demo:self.note.set('DEMO: real browser/robot connections are disabled.');return
        if not self.controller or not self.controller.url:self.note.set('Connect & prepare first to verify the dashboard and tunnel.');return
        webbrowser.open(self.controller.url+('?view='+view if view else ''))

    def stop_drive(self):
        self.cancelled.set()
        if not self.connection:self.note.set('No connection: software Stop cannot reach the robot. Use physical power-off if abnormal.');return
        def work():
            try:self.connection.rpc('stop-drive');self.log('Software Stop request accepted. Observe the physical stop; this is not a hardware emergency stop.')
            except Exception:self.log('Software Stop could not be confirmed. Use reachable physical power-off if abnormal.')
        threading.Thread(target=work,daemon=True).start()

    def service_log(self,name):
        if self.connection:self.run(lambda:self.log(name.upper()+' LOG\n'+self.connection.rpc('logs',name)['text']))

    def save_report(self):
        if self.last is None:self.note.set('Check the connection first.');return
        path=filedialog.asksaveasfilename(title='Save robot status report',defaultextension='.json',initialfile='robot_hub_status.json',filetypes=[('JSON report','*.json')])
        if path:
            try:
                Path(path).write_text(json.dumps(self.last,indent=2),encoding='utf8')
                self.note.set('Status report saved. No password or dashboard bootstrap key is included.')
            except OSError:
                self.note.set('Report could not be saved. Choose a writable location and retry.')

    def close(self):
        if self.closing:return
        if not self.demo and self.connection and not messagebox.askyesno('Disconnect hub','Release the controls and verify the robot is stationary first. Attempt software Stop and disconnect? Remote sensors/base remain running. This does not shut Ubuntu down.'):
            return
        self.closing=True;self.cancelled.set();self.password.set('')
        self.progress.start(12)
        self.progress_text.configure(text='Attempting Stop and disconnecting · please wait')
        connection=self.connection
        def cleanup():
            try:
                if connection:
                    try:connection.rpc('stop-drive')
                    except Exception:pass
                    connection.close()
            finally:self.events.put(('closed',None))
        threading.Thread(target=cleanup,daemon=True).start()
        def finish():
            try:
                kind,value=self.events.get_nowait()
                if kind=='closed':self.root.destroy();return
            except queue.Empty:pass
            self.root.after(50,finish)
        self.note.set('Disconnecting. If the robot behaves abnormally, use physical power-off.')
        self.root.after(50,finish)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--demo',action='store_true',help='Explicit offline simulation; no robot/network/credentials')
    args=parser.parse_args()
    root=tk.Tk()
    App(root,args.demo)
    root.mainloop()


if __name__=='__main__':main()
