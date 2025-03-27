import yt_dlp
import os

def download_instagram_video(url, output_dir="downloads"):
    """
    Baixa um vídeo do Instagram usando yt-dlp.
    
    Args:
        url (str): URL do post do Instagram (ex: https://www.instagram.com/p/Cr6WZqyJQ4T/)
        output_dir (str): Pasta onde o vídeo será salvo (padrão: "downloads")
    """
    # Configurações do yt-dlp
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),  # Nome do arquivo de saída
        'quiet': False,  # Mostra logs no terminal
        'no_warnings': False,  # Exibe avisos (útil para debug)
        'format': 'best',  # Baixa a melhor qualidade disponível
    }

    # Cria a pasta de downloads se não existir
    os.makedirs(output_dir, exist_ok=True)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"✅ Vídeo baixado com sucesso em: {output_dir}")
            print(f"📌 Título: {info.get('title', 'Sem título')}")
            print(f"📌 Duração: {info.get('duration', 'N/A')} segundos")
    except Exception as e:
        print(f"❌ Erro ao baixar o vídeo: {e}")

if __name__ == "__main__":
            self.root.iconbitmap("icon.ico")  # Substitua pelo caminho correto

    # Solicita a URL do vídeo
    video_url = input("🔗 Cole a URL do vídeo do Instagram: ").strip()
    download_instagram_video(video_url)