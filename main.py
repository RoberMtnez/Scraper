import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

class BaseScraper:
    def __init__(self, start_url, max_pages=10):
        self.start_url = start_url
        self.max_pages = max_pages
        self.visited_urls = set()
        self.urls_to_visit = deque([start_url])
        self.session = requests.Session()
        
        # Headers por defecto para simular un navegador estándar
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Guardar el dominio original para no salirnos de la web
        self.domain = urlparse(start_url).netloc

    def run(self):
        print(f"[*] Iniciando scraper en: {self.start_url}")
        pages_scraped = 0

        # Ciclo principal (Breadth-First Search)
        while self.urls_to_visit and pages_scraped < self.max_pages:
            current_url = self.urls_to_visit.popleft()

            if current_url in self.visited_urls:
                continue

            print(f"[{pages_scraped + 1}/{self.max_pages}] Analizando: {current_url}")
            
            try:
                response = self.session.get(current_url, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f" -> Error al obtener la página: {e}")
                self.visited_urls.add(current_url)
                continue

            # Marcar la URL como visitada
            self.visited_urls.add(current_url)
            
            # Parsear el HTML con BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Extraer la información que te interese de esta página
            self.extract_data(soup, current_url)

            # 2. Buscar nuevos enlaces para seguir navegando
            self.discover_links(soup, current_url)
            
            pages_scraped += 1

        print("\n[*] Proceso de scraping finalizado.")

    def extract_data(self, soup, url):
        """
        Método a personalizar. Aquí defines qué datos quieres sacar de la página.
        """
        title = soup.title.string.strip() if soup.title and soup.title.string else 'Sin título'
        print(f" -> Dato extraído (Título): {title}")
        
        # Ejemplo: Extraer todos los h1
        # h1s = [h1.text.strip() for h1 in soup.find_all('h1')]
        # print(f" -> H1s encontrados: {h1s}")
        
        # Aquí también podrías guardar los datos en un CSV, JSON, Base de Datos, etc.

    def discover_links(self, soup, current_url):
        """
        Busca enlaces en la página y los añade a la cola si cumplen los requisitos.
        """
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Construir la URL completa (por si es un enlace relativo como '/contacto')
            full_url = urljoin(current_url, href)
            
            # Eliminar fragmentos (ej: url.com/pagina#seccion)
            full_url = full_url.split('#')[0]

            # Si es un enlace válido y no lo hemos procesado ya, lo encolamos
            if self.is_valid_url(full_url):
                if full_url not in self.visited_urls and full_url not in self.urls_to_visit:
                    self.urls_to_visit.append(full_url)

    def is_valid_url(self, url):
        """
        Verifica que la URL pertenezca al mismo dominio base para no salir del sitio.
        """
        parsed = urlparse(url)
        return parsed.netloc == self.domain and parsed.scheme in ('http', 'https')

def main():
    parser = argparse.ArgumentParser(description="Base para un scraper multipágina en Python.")
    
    # Parámetro obligatorio: URL
    parser.add_argument("url", help="URL inicial desde donde empezar a scrapear.")
    
    # Parámetro opcional: Límite de páginas
    parser.add_argument("--max-pages", type=int, default=10, help="Límite máximo de páginas a analizar (por defecto: 10).")
    
    args = parser.parse_args()

    # Ejecutar el scraper
    scraper = BaseScraper(args.url, max_pages=args.max_pages)
    scraper.run()

if __name__ == "__main__":
    main()
