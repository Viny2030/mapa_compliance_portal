import os
import asyncio
from playwright.async_api import async_playwright

URL = "https://mapacompliance-production.up.railway.app/index-pt.html"
CARPETA = "album_capturas"


async def capturar_album():
    os.makedirs(CARPETA, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        print("Cargando la página...")
        await page.goto(URL, wait_until="networkidle")

        # Espera de 4 segundos para asegurar la renderización de mapas o animaciones
        await page.wait_for_timeout(4000)

        # 1. Capturar la vista completa
        path_full = os.path.join(CARPETA, "vista_completa.png")
        await page.screenshot(path=path_full, full_page=True)
        print(f"Guardada vista completa: {path_full}")

        # 2. Capturar componentes individuales (canvas, svg, secciones)
        elementos = await page.query_selector_all("canvas, svg, main, section, div[class*='map'], div[class*='card']")
        print(f"Se identificaron {len(elementos)} componentes visuales.")

        idx = 1
        for elem in elementos:
            try:
                box = await elem.bounding_box()
                # Filtrar elementos invisibles o demasiado pequeños
                if box and box["width"] > 120 and box["height"] > 120:
                    path_elem = os.path.join(CARPETA, f"componente_{idx}.png")
                    await elem.screenshot(path=path_elem)
                    print(f"Guardado componente {idx}: {path_elem}")
                    idx += 1
            except Exception:
                continue

        await browser.close()
    print(f"\n¡Listo! Revisa la carpeta '{CARPETA}'.")


if __name__ == "__main__":
    asyncio.run(capturar_album())