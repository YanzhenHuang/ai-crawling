import os
import asyncio
from typing import List

from crawl4ai import (AsyncWebCrawler, CrawlResult, BrowserConfig, CrawlerRunConfig, DefaultMarkdownGenerator, PruningContentFilter)

def demo(msg: str):
	"""
	Demo decorator factory.
	:param msg: Message to print before the function is called.
	"""
	def decorator(f):
		async def wrap(*args, **kwargs):
			print(f"\n>>> \033[32m{msg}\033[0m <<<\n")
			return await f(*args, **kwargs)
		return wrap
	return decorator

def save(des: str, content) -> None:
	with open(des, "w") as f:
		for line in content.split("\n"):
			f.write(f"{line}\n")


def log_error(msg: str):
	print(f"\033[31m{msg}\033[0m")


@demo("Demo 1: Basic web crawling.")
async def demo_basic_crawl(save_dir: str, file_name: str):
	"""
	Demo 1: Basic web crawling.
	:param save_dir: The directory to save the crawled files.
	:param file_name: The file name to save the crawled files.
	"""

	if not os.path.exists(save_dir):
		os.makedirs(save_dir)
	
	file_path = os.path.join(save_dir, f"{file_name}.md")
    
	async with AsyncWebCrawler() as crawler:
		results: List[CrawlResult] = await crawler.arun(
			url="https://news.ycombinator.com"
		)
		
		for i, result in enumerate(results):
			print(f"Result {i} Success: {result.success}")
			if result.success:
				md = result.markdown
				save(des=file_path, content=md)
			else:
				print(f"Error crawling this url.")


@demo("Demo 2: Parallel Crawling.")
async def demo_parallel_craw(save_dir: str, file_name: str):
	"""
	Demo 2: Parallel crawling.
	:param save_dir: The directory to save the crawled files.
	:param file_name: The file name to save the crawled files.
	"""

	if not os.path.exists(save_dir):
		os.makedirs(save_dir)
	
	# file_path = os.path.join(save_dir, file_name)

	urls = [
		"https://news.ycombinator.com/",
		"https://example.com",
		"https://httpbin.org/html",
	]

	async with AsyncWebCrawler() as crawler:
		results: List[CrawlResult] = await crawler.arun_many(urls=urls)

		for i, result in enumerate(results):
			file_path = os.path.join(save_dir, f"{file_name}_url-{i}.md")

			print(f"Result {i} ", end=" ")
			if result.success:
				print("Success")
				save(des=file_path, content=result.markdown.raw_markdown)
			else:
				log_error(f"Failed.")


@demo("Demo 3: Fit Markdown")
async def demo_fit_markdown(save_dir: str, file_name: str):
	"""
	Generate **focused** markdown with LLM content filter.
	:param save_dir: The directory to save the crawled files.
	:param file_name: The file name to save the crawled files.
	"""

	file_path_raw, file_path_fit = [os.path.join(save_dir, f"{file_name}_{t}.md") for t in ["raw", "fit"]]
	
	async with AsyncWebCrawler() as crawler:
		result: CrawlResult = await crawler.arun(
			url="https://en.wikipedia.org/wiki/Python_(programming_language)",
			config=CrawlerRunConfig(
				markdown_generator=DefaultMarkdownGenerator(
					content_filter=PruningContentFilter()
				),
			),
		)

		if not result.success:
			log_error("Failed to crawl the website.")
			return

		save(des=file_path_raw, content=result.markdown.raw_markdown)
		save(des=file_path_fit, content=result.markdown.fit_markdown)
		print(f"Raw size: {len(result.markdown.raw_markdown)}\nFit size: {len(result.markdown.fit_markdown)}")


if __name__ == "__main__":
	asyncio.run(demo_basic_crawl("saved_md/demo", "Demo-1_basic_crawl"))
	asyncio.run(demo_parallel_craw("saved_md/demo", "Demo-2_parallel_craw"))
	asyncio.run(demo_fit_markdown("saved_md/demo", "Demo-3_fit_markdown"))
