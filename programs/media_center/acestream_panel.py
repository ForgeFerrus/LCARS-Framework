import re
import socket
import urllib.request
import urllib.parse

from lcars.base.type import Matrix, VBoxLayout, HBoxLayout, Directive, Chassis, Visual
from lcars.base.default import TitanPalette, FontStyle
from lcars.base.components import LCARSButton, style_lcars_scroll_area
from lcars.base.interface import LCARSInput
from lcars.system.board_computer import Computer as get_computer
from programs.media_center.stream_panel import InterceptingWebEnginePage

class AceFinderThread(Directive.Thread):
    results_ready = Directive.Signal(list)
    log_message   = Directive.Signal(str)
    
    def __init__(self, query: str):
        super().__init__()
        self.query = query
        self.computer = get_computer()
        
    def run(self):
        q = self.query
        streams = []
        
        # 1. AI Mistral Search
        prompt = f"Find AceStream P2P links for: {q}. Return raw URLs only."
        
        try:
            self.log_message.emit("◤ [STAGE 1] ESTABLISHING UPLINK TO AI SUBSYSTEM (MISTRAL)...")
            self.log_message.emit("◤ [HEARTBEAT] SYNCING NEURAL PATHWAYS...")
            
            # AI call with non-blocking timeout
            import concurrent.futures
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            future = executor.submit(self.computer.ai.ask, prompt)
            try:
                ai_res = future.result(timeout=25) 
            except concurrent.futures.TimeoutError:
                self.log_message.emit("◤ AI UPLINK TIMEOUT. PROCEEDING TO SCRAPER FALLBACK...")
                ai_res = ""
            finally:
                executor.shutdown(wait=False) # CRITICAL: Don't block the search if AI hangs
            
            if ai_res:
                self.log_message.emit("◤ [STAGE 2] AI RESPONSE RECEIVED. ANALYZING DATA STREAM...")
                self.log_message.emit("◤ [HEARTBEAT] DECODING P2P HASH PATTERNS...")
                
                # Parse AI results
                for line in ai_res.split('\n'):
                    if 'acestream://' in line:
                        match = re.search(r'acestream://([a-fA-F0-9]{40})', line)
                        if match:
                            streams.append({'hash': match.group(1), 'source': 'MISTRAL', 'desc': f"AI Seed: {q}"})
        except Exception as e:
            self.log_message.emit(f"◤ AI SUBSYSTEM ERROR: {str(e)}")

        # 2. Programmatic Scraper Fallback
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            self.log_message.emit("◤ [STAGE 3] ACTIVATING PROGRAMMATIC SCRAPER SUBSYSTEM...")
            self.log_message.emit("◤ [HEARTBEAT] PROBING EXTERNAL INDEXERS (DUCKDUCKGO)...")
            
            ddg_url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(f"{q} acestream hash")
            req = urllib.request.Request(ddg_url, headers=headers)
            html = urllib.request.urlopen(req, timeout=12).read().decode('utf-8', errors='ignore')
            
            self.log_message.emit("◤ [STAGE 4] WEB DATA CAPTURED. EXTRACTING HEXADECIMAL SIGNATURES...")
            
            found_hashes = set()
            # Try to find hashes and some context text around them
            # We look for 40-char hex strings
            raw_results = re.findall(r'([a-fA-F0-9]{40})', html)
            
            for h in raw_results:
                if h not in found_hashes:
                    # Try to find some context in the surrounding 100 chars
                    pos = html.find(h)
                    context_snippet = html[max(0, pos-150):pos].strip()
                    # Clean up HTML tags from snippet
                    context_snippet = re.sub(r'<[^>]+>', '', context_snippet)
                    # Get last 60 chars of cleaned snippet
                    clean_desc = context_snippet[-80:].strip()
                    if not clean_desc: clean_desc = f"P2P NODE {h[:8]}"
                    
                    streams.append({'hash': h, 'source': 'SCRAPER', 'desc': clean_desc})
                    found_hashes.add(h)
        except Exception as e:
            self.log_message.emit(f"◤ SCRAPER FAILURE: {str(e)}")
            
        unique_streams = {v['hash']: v for v in streams}.values()
        self.log_message.emit(f"◤ SCAN COMPLETE. {len(unique_streams)} ANOMALIES FILTERED.")
        self.results_ready.emit(list(unique_streams))


# Панель P2P AceStream — пошук та відтворення стрімів
class AceStreamPanel(Matrix):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.computer = get_computer()
        self._build_ui()

    def _build_ui(self):
        c_prim = TitanPalette.Buttons[0]
        c_sec  = TitanPalette.Buttons[2]
        c_tert = TitanPalette.YellowAlert[0]

        lay = VBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        self.splitter = Chassis.Splitter(Directive.Protocol.Orientation.Horizontal)
        self.splitter.setHandleWidth(4)
        self.splitter.setStyleSheet("QSplitter::handle { background: #111; }")
        lay.addWidget(self.splitter, 1)

        # --- LEFT SIDE ---
        left_panel = Matrix()
        left_lay = VBoxLayout(left_panel)
        left_lay.setContentsMargins(0, 0, 0, 0)

        lbl_head = Visual.Label("◤ P2P STREAM DISCOVERY")
        lbl_head.setStyleSheet(FontStyle(24, "normal") + f"color: {c_sec}; margin-bottom: 8px;")
        left_lay.addWidget(lbl_head)

        search_box = HBoxLayout()
        self.search_input = LCARSInput(c_tert)
        self.search_input.setPlaceholderText("MATCH OR EVENT NAME...")
        self.search_input.returnPressed.connect(self._start_search)
        search_box.addWidget(self.search_input, 1)

        self.btn_search = LCARSButton("SCAN", c_prim, shape="rect")
        self.btn_search.clicked.connect(self._start_search)
        self.btn_search.setMinimumSize(100, 50)
        search_box.addWidget(self.btn_search)
        left_lay.addLayout(search_box)

        self.console = Visual.Text()
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(150)
        self.console.setMaximumHeight(350)
        self.console.setSizePolicy(Chassis.SizePolicy.Policy.Expanding, Chassis.SizePolicy.Policy.Preferred)
        self.console.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #050505; color: {c_prim};
                border: none; margin: 0px; padding: 12px;
                {FontStyle(18, "normal")}
            }}
            QScrollBar:vertical {{ border: none; background: #000; width: 14px; }}
            QScrollBar::handle:vertical {{ background: {c_sec}; border-radius: 0px; min-height: 50px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        self.console.setPlaceholderText("◤ SUBSPACE SCANNER LOGS...")
        left_lay.addWidget(self.console)

        self.scroll_area = Chassis.ScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(Chassis.Frame.Shape.NoFrame)
        self.scroll_area.setLineWidth(0)
        style_lcars_scroll_area(self.scroll_area, hide_bars=False)

        self.list_container = Matrix()
        self.list_container.setStyleSheet("background: transparent; border: none;")
        self.list_lay = VBoxLayout(self.list_container)
        self.list_lay.setAlignment(Directive.Align.AlignTop)
        self.list_lay.setContentsMargins(0, 10, 5, 0)
        self.list_lay.setSpacing(12)

        self.scroll_area.setWidget(self.list_container)
        left_lay.addWidget(self.scroll_area, 1)
        self.splitter.addWidget(left_panel)

        # --- RIGHT SIDE ---
        right_panel = Matrix()
        right_lay = VBoxLayout(right_panel)
        right_lay.setContentsMargins(10, 0, 0, 0)

        self.lbl_current_stream = Visual.Label("NO STREAM ACTIVE")
        self.lbl_current_stream.setStyleSheet(FontStyle(28, "normal") + f"color: {c_prim};")
        self.lbl_current_stream.setMinimumHeight(50)
        self.lbl_current_stream.setAlignment(Directive.Align.AlignCenter)
        right_lay.addWidget(self.lbl_current_stream)

        self.lbl_engine_status = Visual.Label("◤ PROXY CHECKING...")
        self.lbl_engine_status.setStyleSheet(FontStyle(14) + "color: #444;")
        self.lbl_engine_status.setAlignment(Directive.Align.AlignRight)
        right_lay.addWidget(self.lbl_engine_status)
        Directive.Timer.singleShot(1000, self._check_engine)

        self.webview = Directive.WebView()
        self.webview.page().setBackgroundColor(Directive.Protocol.GlobalColor.black)

        s = Directive.WebScript()
        s.setName("ForceBlackBackground")
        s.setSourceCode("document.documentElement.style.backgroundColor = 'black'; document.body.style.backgroundColor = 'black';")
        s.setInjectionPoint(Directive.WebScript.InjectionPoint.DocumentReady)
        s.setWorldId(Directive.WebScript.ScriptWorldId.MainWorld)
        s.setRunsOnSubFrames(True)
        self.webview.page().scripts().insert(s)

        self.webview.setHtml("<html><body style='background-color:black; color:white;'>◤ INITIALIZING BIOS STREAM...</body></html>")
        self.webview.setStyleSheet("background-color: black; border: none; border-radius: 0px;")
        self.webview.setPage(InterceptingWebEnginePage(self.webview))
        right_lay.addWidget(self.webview, 1)

        btn_stop = LCARSButton("STOP STREAM", TitanPalette.RedAlert[0], shape="pill")
        btn_stop.clicked.connect(self._stop_stream)
        right_lay.addWidget(btn_stop, 0, Directive.Align.AlignCenter)

        self.splitter.addWidget(right_panel)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 7)

    def _start_search(self):
        q = self.search_input.text().strip()
        if not q: return
        self._clear_list()
        self.console.clear()
        self.search_input.setEnabled(False)
        self.btn_search.setText("SCANNING...")

        self.search_thread = AceFinderThread(q)
        self.search_thread.results_ready.connect(self._on_search_results)
        self.search_thread.log_message.connect(self._add_log)
        self.search_thread.start()

    def _add_log(self, msg: str):
        self.console.appendPlainText(msg)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def _clear_list(self):
        while self.list_lay.count():
            item = self.list_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

    def _on_search_results(self, streams: list):
        self.search_input.setEnabled(True)
        self.btn_search.setText("SCAN")
        self._clear_list()

        if not streams:
            err = Visual.Label("NO P2P ANOMALIES LOCATED.")
            err.setStyleSheet(FontStyle(16, "normal") + f"color: {TitanPalette.RedAlert[0]};")
            self.list_lay.addWidget(err)
            return

        for i, s in enumerate(streams):
            c = TitanPalette.Buttons[i % len(TitanPalette.Buttons)]
            text = f"◤ SOURCE: {s['source']}\n{s['desc']}"
            btn = LCARSButton(text, c, font_size=18, font_weight="normal")
            btn.setMinimumHeight(85)
            btn.clicked.connect(lambda ch, h=s['hash'], d=s['desc']: self._play_stream(h, d))
            self.list_lay.addWidget(btn)

    def _play_stream(self, hash_id: str, description: str):
        self.lbl_current_stream.setText(f"PLAYING: {description.upper()}")
        url = f"http://127.0.0.1:6878/ace/getstream?id={hash_id}&.mp4"
        self.webview.setUrl(Directive.Url(url))
        self._add_log(f"▤ ACTIVATING P2P STREAM: {hash_id}")

    def _stop_stream(self):
        self.webview.setUrl(Directive.Url("about:blank"))
        self.lbl_current_stream.setText("NO STREAM ACTIVE")

    def stop_all(self):
        self._stop_stream()

    # Перевіряємо чи AceStream engine доступний на локальному порту
    def _check_engine(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('127.0.0.1', 6878))
        s.close()

        if result == 0:
            self.lbl_engine_status.setText('◤ P2P UPLINK: STABLE')
            self.lbl_engine_status.setStyleSheet(FontStyle(12) + 'color: #00FF00;')
        else:
            self.lbl_engine_status.setText('▤ P2P UPLINK: OFFLINE (ENGINE REQUIRED)')
            self.lbl_engine_status.setStyleSheet(FontStyle(12) + 'color: #CC3333;')

        Directive.Timer.singleShot(10000, self._check_engine)
