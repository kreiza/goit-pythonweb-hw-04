import asyncio
import argparse
import logging
from pathlib import Path
import aiofiles
import aiofiles.os


async def read_folder(source_path: Path, output_path: Path):
    """Рекурсивно читає всі файли у вихідній папці та копіює їх у цільову папку."""
    tasks = []
    
    for item in source_path.rglob('*'):
        if item.is_file():
            tasks.append(copy_file(item, output_path))
    
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def copy_file(file_path: Path, output_path: Path):
    """Копіює файл у відповідну підпапку на основі розширення."""
    try:
        extension = file_path.suffix.lower() or 'no_extension'
        extension = extension.lstrip('.')
        
        target_dir = output_path / extension
        await aiofiles.os.makedirs(target_dir, exist_ok=True)
        
        target_file = target_dir / file_path.name
        
        async with aiofiles.open(file_path, 'rb') as src:
            async with aiofiles.open(target_file, 'wb') as dst:
                await dst.write(await src.read())
        
        logging.info(f"Скопійовано: {file_path} -> {target_file}")
        
    except Exception as e:
        logging.error(f"Помилка копіювання {file_path}: {e}")


async def main():
    parser = argparse.ArgumentParser(description='Асинхронне сортування файлів за розширеннями')
    parser.add_argument('source', help='Вихідна папка')
    parser.add_argument('output', help='Цільова папка')
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    output_path = Path(args.output)
    
    if not source_path.exists():
        logging.error(f"Вихідна папка не існує: {source_path}")
        return
    
    await aiofiles.os.makedirs(output_path, exist_ok=True)
    
    logging.info(f"Початок сортування з {source_path} до {output_path}")
    await read_folder(source_path, output_path)
    logging.info("Сортування завершено")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())