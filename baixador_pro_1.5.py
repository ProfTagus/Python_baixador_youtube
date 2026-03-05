import yt_dlp
import os
import sys
import subprocess
from pathlib import Path


def verificar_deno():
    """Verifica se o Deno está instalado e orienta o usuário se não estiver"""
    try:
        # Tenta executar deno --version para verificar se está instalado
        subprocess.run(['deno', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def instalar_deno():
    """Mostra instruções para instalar o Deno"""
    print("\n" + "="*70)
    print("🔴 DENO NÃO ENCONTRADO!")
    print("="*70)
    print("\nPara melhor funcionamento do yt-dlp, é recomendado instalar o Deno:")
    print("\n📦 Instalação:")
    print("   • Windows (PowerShell como administrador):")
    print("     irm https://deno.land/install.ps1 | iex")
    print("\n   • Linux/macOS:")
    print("     curl -fsSL https://deno.land/install.sh | sh")
    print("\n   • Ou baixe do site oficial: https://deno.com/")
    print("\n💡 Após instalar, reinicie o terminal e execute este programa novamente.")
    print("\n⚠️  Por enquanto, o download continuará sem o Deno (pode funcionar, mas com limitações)")
    print("="*70)

    resposta = input("\nDeseja continuar mesmo assim? (s/n): ").strip().lower()
    return resposta in ['s', 'sim', 's']


def baixar(url, tipo):
    """
    Função responsável por configurar e executar o download.
    Recebe:
    - url: link do YouTube
    - tipo: '1' para vídeo / '2' para áudio
    """

    # 🔹 Verifica se o Deno está instalado (opcional, mas recomendado)
    deno_instalado = verificar_deno()
    if not deno_instalado:
        if not instalar_deno():
            print("\n⏹️ Download cancelado pelo usuário.")
            return False

    # 🔹 Cria a pasta base Downloads
    pasta_base = 'Downloads'
    if not os.path.exists(pasta_base):
        os.makedirs(pasta_base)

    # 🔹 Configurações base do yt_dlp com suporte a JavaScript runtime
    opcoes = {
        'outtmpl': f'{pasta_base}/%(title)s.%(ext)s',
        'progress_hooks': [progresso],
        'ignoreerrors': False,
        'quiet': False,
        'no_warnings': False,
        'extractor_args': {
            'youtube': [
                # Habilita runtime JavaScript para resolver desafios do YouTube
                'js-runtime=deno' if deno_instalado else 'js-runtime=none',
                # Permite baixar scripts EJS do npm (necessário para Deno)
                'remote-ejs=npm'
            ]
        }
    }

    # 🔹 Configurações específicas por tipo de download
    if tipo == '1':
        opcoes['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        print("\n🎬 Modo selecionado: VÍDEO (MP4)")
        extensao = 'mp4'
    else:
        opcoes['format'] = 'bestaudio/best'
        opcoes['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        print("\n🎵 Modo selecionado: ÁUDIO (MP3)")
        extensao = 'mp3'

    try:
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            # 🔹 Extrai informações sem baixar
            print("\n🔍 Analisando link...")
            info = ydl.extract_info(url, download=False)

            # 🔹 Verifica se é playlist
            if 'entries' in info:
                return processar_playlist(info, url, tipo, extensao, ydl)
            else:
                return baixar_video_unico(info, tipo, extensao, ydl)

    except Exception as e:
        print(f"\n❌ Erro durante o processamento: {e}")
        return False


def processar_playlist(info, url, tipo, extensao, ydl):
    """Processa o download de playlists"""

    total_videos = len(info['entries'])
    print("\n" + "="*60)
    print(f"📂 ** PLAYLIST DETECTADA ** 📂")
    print("="*60)
    print(f"\n📊 Estatísticas da playlist:")
    print(f"   • Total de vídeos: {total_videos}")

    # Mostra alguns títulos como exemplo
    print(f"\n📋 Primeiros vídeos:")
    for i, entry in enumerate(info['entries'][:5], 1):
        if entry and entry.get('title'):
            titulo = entry.get('title', 'Título desconhecido')
            duracao = entry.get('duration', 0)
            if duracao:
                minutos = duracao // 60
                segundos = duracao % 60
                print(f"   {i}. {titulo[:50]}... ({minutos}:{segundos:02d})")
            else:
                print(f"   {i}. {titulo[:50]}...")

    if total_videos > 5:
        print(f"   ... e mais {total_videos - 5} vídeos")

    print("\n" + "="*60)

    # Pergunta ao usuário o que fazer
    while True:
        print("\n🎯 O que você deseja fazer?")
        print("1 - Baixar TODA a playlist")
        print("2 - Escolher UM vídeo específico da playlist")
        print("3 - Cancelar download")

        escolha = input("👉 Digite 1, 2 ou 3: ").strip()

        if escolha == '1':
            return baixar_playlist_completa(info, url, tipo, extensao, ydl)
        elif escolha == '2':
            return perguntar_qual_video_baixar(info, tipo, extensao, ydl)
        elif escolha == '3':
            print("\n⏹️ Download cancelado pelo usuário.")
            return False
        else:
            print("❌ Opção inválida! Digite 1, 2 ou 3.")


def baixar_playlist_completa(info, url, tipo, extensao, ydl):
    """Baixa todos os vídeos da playlist"""

    total_videos = len(info['entries'])
    print(f"\n📥 Iniciando download da playlist com {total_videos} vídeos...")

    # Cria pasta específica para a playlist
    nome_playlist = info.get('title', 'Playlist').replace(
        '/', '_').replace('\\', '_')
    # Remove caracteres especiais do nome da pasta
    nome_playlist = ''.join(
        c for c in nome_playlist if c.isalnum() or c in ' -_').strip()
    pasta_playlist = os.path.join(
        'Downloads', f"Playlist - {nome_playlist[:50]}")

    # Atualiza o template de saída para usar a pasta da playlist
    ydl.params['outtmpl'] = os.path.join(
        pasta_playlist, '%(playlist_index)03d - %(title)s.%(ext)s')

    if not os.path.exists(pasta_playlist):
        os.makedirs(pasta_playlist)

    print(f"📁 Salvando em: {pasta_playlist}")

    try:
        ydl.download([url])
        print(f"\n✅ Playlist baixada com sucesso em: {pasta_playlist}")
        return True
    except Exception as e:
        print(f"\n❌ Erro ao baixar playlist: {e}")
        return False


def perguntar_qual_video_baixar(info, tipo, extensao, ydl):
    """Permite ao usuário escolher um vídeo específico da playlist"""

    total_videos = len(info['entries'])

    while True:
        print(f"\n🎯 Escolha um vídeo (1 a {total_videos}) ou 0 para cancelar:")
        try:
            escolha = int(input("👉 Número do vídeo: "))

            if escolha == 0:
                print("\n⏹️ Operação cancelada.")
                return False

            if 1 <= escolha <= total_videos:
                video_escolhido = info['entries'][escolha - 1]
                if not video_escolhido:
                    print("❌ Vídeo não disponível. Tente outro.")
                    continue

                titulo = video_escolhido.get('title', 'Título desconhecido')
                print(f"\n📥 Baixando: {titulo}")

                # Pega a URL do vídeo específico
                url_video = video_escolhido.get('webpage_url')
                if url_video:
                    ydl.download([url_video])
                    print("\n✅ Download concluído!")
                    return True
                else:
                    print("❌ Não foi possível obter a URL do vídeo.")
                    return False
            else:
                print(f"❌ Número inválido! Escolha entre 1 e {total_videos}.")
        except ValueError:
            print("❌ Digite apenas números!")


def baixar_video_unico(info, tipo, extensao, ydl):
    """Baixa um único vídeo"""

    titulo = info.get('title', 'Título desconhecido')
    duracao = info.get('duration', 0)
    if duracao:
        minutos = duracao // 60
        segundos = duracao % 60
        print(f"\n🎥 Vídeo encontrado: {titulo}")
        print(f"⏱️ Duração: {minutos}:{segundos:02d}")
    else:
        print(f"\n🎥 Vídeo encontrado: {titulo}")

    # Pergunta confirmação
    while True:
        resp = input("\n📥 Deseja baixar este vídeo? (s/n): ").strip().lower()
        if resp in ['s', 'sim', 's']:
            print("\n📥 Iniciando download...")
            try:
                ydl.download([info['webpage_url']])
                print("\n✅ Download concluído!")
                return True
            except Exception as e:
                print(f"\n❌ Erro no download: {e}")
                return False
        elif resp in ['n', 'não', 'nao', 'n']:
            print("\n⏹️ Download cancelado.")
            return False
        else:
            print("❌ Responda com 's' ou 'n'")


def progresso(d):
    """
    Função chamada automaticamente durante o download.
    Mostra progresso em tempo real.
    """
    if d['status'] == 'downloading':
        percentual = d['_percent_str'].strip()
        velocidade = d.get('_speed_str', '?').strip()
        tamanho = d.get('_total_bytes_str', '?').strip()
        eta = d.get('_eta_str', '?').strip()

        # Mostra também o índice do vídeo se for playlist
        if 'playlist_index' in d:
            playlist_idx = d['playlist_index']
            playlist_size = d.get('playlist_count', '?')
            print(
                f"📹 [{playlist_idx}/{playlist_size}] ⏳ {percentual} de {tamanho} | {velocidade} | ETA: {eta}   ", end='\r')
        else:
            print(
                f"⏳ {percentual} de {tamanho} | {velocidade} | ETA: {eta}   ", end='\r')

    elif d['status'] == 'finished':
        print("\n🔄 Processando arquivo...")


def main():
    """Função principal do programa"""

    print("="*70)
    print("🎥🎵 YOUTUBE DOWNLOADER PROFISSIONAL - COM SUPORTE A JS RUNTIME 🎵🎥")
    print("="*70)
    print("\n💡 Recursos:")
    print("   • Download de vídeos individuais")
    print("   • Download de playlists completas")
    print("   • Escolha de vídeo específico da playlist")
    print("   • Formato: MP4 (vídeo) ou MP3 (áudio)")
    print("   • Suporte a JavaScript runtime (Deno) para melhor compatibilidade")
    print("="*70)

    # Verificação inicial do Deno
    deno_instalado = verificar_deno()
    if deno_instalado:
        print("\n✅ Deno encontrado! O download terá melhor compatibilidade.")
    else:
        print("\n⚠️  Deno não encontrado. O download pode funcionar, mas com limitações.")
        print("   Recomenda-se instalar o Deno para melhor experiência.")

    while True:
        # 🔹 Solicita URL ao usuário
        print("\n" + "-"*70)
        url = input(
            "📎 Cole o link do YouTube (ou 'sair' para encerrar): ").strip()

        if url.lower() in ['sair', 'exit', 'quit', 'q']:
            print("\n👋 Programa encerrado. Até mais!")
            break

        if not url:
            print("❌ URL não pode estar vazia!")
            continue

        # 🔹 Menu de escolha do formato
        print("\n📦 Escolha o formato de download:")
        print("1 - Vídeo (MP4)")
        print("2 - Áudio (MP3)")
        escolha = input("👉 Digite 1 ou 2: ").strip()

        if escolha in ['1', '2']:
            baixar(url, escolha)
        else:
            print("❌ Opção inválida! Digite apenas 1 ou 2.")

        print("\n" + "="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
