import customtkinter as ctk
import yt_dlp
import os
import re
import webbrowser
import threading
from tkinter import messagebox, filedialog
from datetime import datetime

class VideoDownloaderApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Rutracore's Video Downloader")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        self.root.iconbitmap("icon.ico")  # Substitua pelo caminho correto

        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Configurações
        self.download_folder = os.path.join(os.path.expanduser("~"), "Videos", "Rutracore Downloads")
        self.history_file = os.path.join(self.download_folder, "download_history.txt")
        self.favorites_file = os.path.join(self.download_folder, "favorites.txt")
        
        # Garante que o diretório existe
        os.makedirs(self.download_folder, exist_ok=True)
        
        # Variáveis de controle
        self.download_thread = None
        self.stop_download = False
        
        self.create_widgets()
        self.load_history()
        self.load_favorites()
        self.root.mainloop()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Cabeçalho
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(pady=(10, 5), fill="x")
        
        ctk.CTkLabel(
            header_frame, 
            text="Rutracore's Video Downloader",
            font=("Arial", 20, "bold")
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_frame,
            text="v2.0",
            text_color="gray70",
            font=("Arial", 10)
        ).pack(side="right", padx=5)
        
        # Abas
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)
        self.tabview.add("Download")
        self.tabview.add("Histórico")
        self.tabview.add("Favoritos")
        
        # Tab Download
        self.create_download_tab()
        
        # Tab Histórico
        self.create_history_tab()
        
        # Tab Favoritos
        self.create_favorites_tab()
    
    def create_download_tab(self):
        tab = self.tabview.tab("Download")
        
        # Campo de URL
        url_frame = ctk.CTkFrame(tab, fg_color="transparent")
        url_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(url_frame, text="URL do vídeo:").pack(anchor="w")
        self.url_entry = ctk.CTkEntry(
            url_frame, 
            placeholder_text="https://www.youtube.com/watch?... ou https://instagram.com/p/...",
            width=550
        )
        self.url_entry.pack(pady=5)
        
        # Opções de download
        options_frame = ctk.CTkFrame(tab, fg_color="transparent")
        options_frame.pack(pady=10, padx=10, fill="x")
        
        # Qualidade
        ctk.CTkLabel(options_frame, text="Qualidade:").grid(row=0, column=0, sticky="w")
        qualities = ["Melhor disponível", "1080p", "720p", "480p", "360p", "Apenas áudio"]
        self.quality_var = ctk.StringVar(value=qualities[0])
        self.quality_menu = ctk.CTkOptionMenu(
            options_frame,
            values=qualities,
            variable=self.quality_var
        )
        self.quality_menu.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Formato
        ctk.CTkLabel(options_frame, text="Formato:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.format_var = ctk.StringVar(value="mp4")
        formats = ["MP4 (vídeo)", "MP3 (áudio)", "WEBM"]
        self.format_menu = ctk.CTkOptionMenu(
            options_frame,
            values=formats,
            variable=self.format_var
        )
        self.format_menu.grid(row=1, column=1, padx=5, pady=(10, 0), sticky="ew")
        
        # Pasta de destino
        dir_frame = ctk.CTkFrame(tab, fg_color="transparent")
        dir_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(dir_frame, text="Pasta de destino:").pack(anchor="w")
        
        # Frame para o caminho da pasta e botão
        path_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        path_frame.pack(fill="x")
        
        self.dir_label = ctk.CTkLabel(
            path_frame,
            text=self.download_folder,
            text_color="gray70",
            wraplength=400,
            justify="left"
        )
        self.dir_label.pack(side="left", fill="x", expand=True)
        
        # Botão para alterar pasta
        ctk.CTkButton(
            path_frame,
            text="Alterar",
            command=self.change_download_folder,
            width=80
        ).pack(side="right", padx=5)
        
        # Botões de ação
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="Abrir Pasta",
            command=self.open_download_folder,
            width=120,
            fg_color="gray30",
            hover_color="gray40"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Baixar Agora",
            command=self.start_download_thread,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#E1306C",
            hover_color="#C13584"
        ).pack(side="right", fill="x", expand=True)
        
        # Progresso
        self.progress_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.progress_frame.pack(pady=10, padx=10, fill="x")
        
        self.status_label = ctk.CTkLabel(self.progress_frame, text="", text_color="gray70")
        self.status_label.pack(pady=5)
        
        self.progress = ctk.CTkProgressBar(self.progress_frame, mode="determinate")
        self.progress.pack(fill="x")
        self.progress.set(0)
        
        self.stop_btn = ctk.CTkButton(
            self.progress_frame,
            text="Cancelar",
            command=self.cancel_download,
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.stop_btn.pack(pady=10)
    
    def change_download_folder(self):
        """Permite ao usuário selecionar uma nova pasta de download"""
        new_folder = filedialog.askdirectory(
            title="Selecione a pasta para salvar os downloads",
            initialdir=self.download_folder
        )
        
        if new_folder:
            self.download_folder = new_folder
            self.dir_label.configure(text=self.download_folder)
            
            # Atualiza os caminhos dos arquivos de histórico e favoritos
            self.history_file = os.path.join(self.download_folder, "download_history.txt")
            self.favorites_file = os.path.join(self.download_folder, "favorites.txt")
            
            # Garante que os arquivos existam na nova localização
            self.load_favorites()
            self.load_history()
            
            self.show_info(f"Pasta de download alterada para:\n{self.download_folder}")

    # ... (o restante do código permanece igual)
    def create_history_tab(self):
        tab = self.tabview.tab("Histórico")
        
        # Controles
        controls_frame = ctk.CTkFrame(tab, fg_color="transparent")
        controls_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkButton(
            controls_frame,
            text="Limpar Histórico",
            command=self.clear_history,
            width=120,
            fg_color="gray30",
            hover_color="gray40"
        ).pack(side="right")
        
        # Lista de histórico
        self.history_list = ctk.CTkTextbox(
            tab,
            wrap="word",
            state="disabled",
            height=300
        )
        self.history_list.pack(pady=10, padx=10, fill="both", expand=True)
    
    def create_favorites_tab(self):
        tab = self.tabview.tab("Favoritos")
        
        # Lista de favoritos
        self.favorites_list = ctk.CTkScrollableFrame(tab)
        self.favorites_list.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Atualiza a lista
        self.update_favorites_display()
    
    def start_download_thread(self):
        """Inicia o download em uma thread separada"""
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showwarning("Aviso", "Já existe um download em andamento!")
            return
        
        self.stop_download = False
        self.download_thread = threading.Thread(target=self.download_video)
        self.download_thread.start()
    
    def download_video(self):
        """Executa o download do vídeo"""
        url = self.url_entry.get().strip()
        
        if not url:
            self.show_error("Por favor, insira a URL do vídeo!")
            return
        
        if not self.is_valid_url(url):
            self.show_error("URL inválida ou não suportada!")
            return
        
        self.set_download_ui_state(True)
        
        try:
            os.makedirs(self.download_folder, exist_ok=True)
            
            # Configurações baseadas nas opções selecionadas
            ydl_opts = {
                'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
                'quiet': True,
                'progress_hooks': [self.update_progress],
                'noprogress': False,
            }
            
            # Configura qualidade
            quality = self.quality_var.get()
            if quality == "Melhor disponível":
                ydl_opts['format'] = 'best'
            elif quality == "Apenas áudio":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }]
            else:
                ydl_opts['format'] = f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]'
            
            # Configura formato
            if self.format_var.get() == "MP3 (áudio)":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Sem título')
                
                # Adiciona ao histórico
                self.add_to_history(title, url)
                
                # Mostra mensagem de sucesso
                self.show_success(
                    "Download completo!",
                    f"✅ {title}\n\n📁 {self.download_folder}"
                )
                
        except Exception as e:
            if not self.stop_download:
                self.show_error(f"Falha ao baixar:\n{str(e)}")
        finally:
            self.set_download_ui_state(False)
            if not self.stop_download:
                self.progress.set(0)
                self.status_label.configure(text="Pronto para novo download", text_color="gray70")
    
    def set_download_ui_state(self, downloading):
        """Atualiza o estado da UI durante o download"""
        state = "disabled" if downloading else "normal"
        self.url_entry.configure(state=state)
        self.quality_menu.configure(state=state)
        self.format_menu.configure(state=state)
        self.stop_btn.configure(state="normal" if downloading else "disabled")
    
    def cancel_download(self):
        """Cancela o download em andamento"""
        self.stop_download = True
        self.status_label.configure(text="Cancelando...", text_color="orange")
        self.stop_btn.configure(state="disabled")
    
    def update_progress(self, d):
        """Atualiza a barra de progresso com tratamento de códigos ANSI"""
        if self.stop_download:
            raise Exception("Download cancelado pelo usuário")
        
        if d['status'] == 'downloading':
            # Remove códigos ANSI da string de porcentagem
            percent_str = re.sub(r'\x1b\[[0-9;]*[mK]', '', d.get('_percent_str', '0%'))
            clean_percent = ''.join(c for c in percent_str if c.isdigit() or c == '.')
            
            try:
                percent = min(100, max(0, float(clean_percent)))
                self.progress.set(percent / 100)
                
                # Remove códigos ANSI da velocidade e tempo restante
                speed = re.sub(r'\x1b\[[0-9;]*[mK]', '', d.get('_speed_str', '?'))
                eta = re.sub(r'\x1b\[[0-9;]*[mK]', '', d.get('_eta_str', '?'))
                
                self.status_label.configure(
                    text=f"Baixando... {percent:.1f}% | Velocidade: {speed.strip()} | Tempo: {eta.strip()}",
                    text_color="white"
                )
            except (ValueError, TypeError):
                self.status_label.configure(
                    text="Baixando... (progresso indisponível)",
                    text_color="white"
                )
                self.progress.set(0)
            
            self.root.update()
    
    def is_valid_url(self, url):
        """Valida se a URL é suportada"""
        supported_domains = [
            'youtube.com', 'youtu.be', 'instagram.com', 'fb.watch',
            'tiktok.com', 'facebook.com','twitter.com', 'twitch.tv',
            'dailymotion.com','xvideos.com', 'xnxx.com','cnnamador.com', 'pornhub.com',
            'camwhores.video'
        ]
        return any(domain in url for domain in supported_domains)
    
    def open_download_folder(self):
        """Abre a pasta de downloads"""
        try:
            os.makedirs(self.download_folder, exist_ok=True)
            webbrowser.open(self.download_folder)
        except Exception as e:
            self.show_error(f"Não foi possível abrir a pasta:\n{str(e)}")
    
    def add_to_history(self, title, url):
        """Adiciona um download ao histórico"""
        try:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            entry = f"[{timestamp}] {title} ({url})\n"
            
            with open(self.history_file, "a", encoding="utf-8") as f:
                f.write(entry)
            
            self.load_history()
        except Exception as e:
            print(f"Erro ao salvar histórico: {str(e)}")
    
    def load_history(self):
        """Carrega o histórico de downloads"""
        try:
            content = ""
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    content = f.read()
            
            self.history_list.configure(state="normal")
            self.history_list.delete("1.0", "end")
            self.history_list.insert("end", content or "Nenhum item no histórico")
            self.history_list.configure(state="disabled")
        except Exception as e:
            print(f"Erro ao carregar histórico: {str(e)}")
    
    def clear_history(self):
        """Limpa o histórico de downloads"""
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
            self.load_history()
            self.show_info("Histórico limpo com sucesso!")
        except Exception as e:
            self.show_error(f"Erro ao limpar histórico:\n{str(e)}")
    
    def load_favorites(self):
        """Carrega os favoritos"""
        try:
            # Cria o arquivo se não existir
            if not os.path.exists(self.favorites_file):
                with open(self.favorites_file, "w", encoding="utf-8") as f:
                    f.write("")
        except Exception as e:
            print(f"Erro ao carregar favoritos: {str(e)}")
    
    def update_favorites_display(self):
        """Atualiza a exibição dos favoritos"""
        for widget in self.favorites_list.winfo_children():
            widget.destroy()
        
        try:
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, "r", encoding="utf-8") as f:
                    for line in f.readlines():
                        if line.strip():
                            self.create_favorite_item(line.strip())
            
            if not self.favorites_list.winfo_children():
                ctk.CTkLabel(
                    self.favorites_list,
                    text="Nenhum favorito adicionado",
                    text_color="gray70"
                ).pack(pady=20)
        except Exception as e:
            print(f"Erro ao carregar favoritos: {str(e)}")
    
    def create_favorite_item(self, entry):
        """Cria um item na lista de favoritos"""
        frame = ctk.CTkFrame(self.favorites_list, corner_radius=5)
        frame.pack(pady=5, padx=5, fill="x")
        
        # Extrai título e URL
        parts = entry.split("|||")
        if len(parts) >= 2:
            title, url = parts[0], parts[1]
        else:
            title, url = entry, entry
        
        # Label com título (com ellipsis para textos longos)
        title_label = ctk.CTkLabel(
            frame,
            text=title[:50] + "..." if len(title) > 50 else title,
            wraplength=400,
            anchor="w",
            justify="left"
        )
        title_label.pack(side="left", padx=10, fill="x", expand=True)
        
        # Botões de ação
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(
            btn_frame,
            text="Baixar",
            width=60,
            command=lambda u=url: self.download_from_favorite(u),
            fg_color="green",
            hover_color="darkgreen"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="Remover",
            width=60,
            command=lambda e=entry: self.remove_favorite(e),
            fg_color="red",
            hover_color="darkred"
        ).pack(side="left", padx=2)
    
    def download_from_favorite(self, url):
        """Preenche a URL a partir de um favorito"""
        self.tabview.set("Download")
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url)
        self.start_download_thread()
    
    def remove_favorite(self, entry):
        """Remove um item dos favoritos"""
        try:
            with open(self.favorites_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            with open(self.favorites_file, "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip() != entry:
                        f.write(line)
            
            self.update_favorites_display()
            self.show_info("Favorito removido com sucesso!")
        except Exception as e:
            self.show_error(f"Erro ao remover favorito:\n{str(e)}")
    
    def add_to_favorites(self, title, url):
        """Adiciona um item aos favoritos"""
        try:
            entry = f"{title}|||{url}\n"
            
            # Verifica se já existe
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, "r", encoding="utf-8") as f:
                    if entry in f.read():
                        self.show_info("Este item já está nos favoritos!")
                        return
            
            with open(self.favorites_file, "a", encoding="utf-8") as f:
                f.write(entry)
            
            self.update_favorites_display()
            self.show_info("Adicionado aos favoritos!")
        except Exception as e:
            self.show_error(f"Erro ao adicionar favorito:\n{str(e)}")
    
    def show_error(self, message):
        """Mostra mensagem de erro"""
        messagebox.showerror("Erro", message)
    
    def show_info(self, message):
        """Mostra mensagem informativa"""
        messagebox.showinfo("Informação", message)
    
    def show_success(self, title, message):
        """Mostra mensagem de sucesso com opção de favoritar"""
        # Cria uma janela personalizada
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Mensagem
        ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=350,
            justify="left"
        ).pack(pady=20, padx=20)
        
        # Botões
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        url = self.url_entry.get().strip()
        title = message.split("\n")[0][2:]  # Extrai o título da mensagem
        
        ctk.CTkButton(
            btn_frame,
            text="Adicionar aos Favoritos",
            command=lambda: [self.add_to_favorites(title, url), dialog.destroy()],
            fg_color="green",
            hover_color="darkgreen"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="OK",
            command=dialog.destroy,
            width=100
        ).pack(side="right", padx=10)

if __name__ == "__main__":
    app = VideoDownloaderApp()