import os, asyncio, json
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
			if "save_dir" in kwargs and not os.path.exists(kwargs["save_dir"]):
				os.makedirs(kwargs["save_dir"])
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


@demo("Demo 4: Media and Links")
async def demo_media_and_links(save_dir: str, file_name: str):
	file_path = os.path.join(save_dir, f"{file_name}.json")
	async with AsyncWebCrawler() as crawler:
		results: List[CrawlResult] = await crawler.arun(url="https://en.wikipedia.org/wiki/Python_(programming_language)")

		for i, result in enumerate(results):
			if not result.success:
				log_error(f"Result {i}: Failed to crawl.")
				continue

			images = result.media.get("images", [])
			internal_links = result.links.get("internal", [])
			external_links = result.links.get("external", [])

			out = {
				"images": [image["src"] for image in images],
				"internal_links": [ilink["href"] for ilink in internal_links],
				"external_links": [elink["href"] for elink in external_links],
			}

			with open(file_path, "w") as f:
				json.dump(out, f, indent=4)

			print(
				f"Found"
				f"Images: {len(images)}\n"
				f"Internal Links: {len(internal_links)}\n"
				f"External Links: {len(external_links)}\n"
			)


if __name__ == "__main__":
	asyncio.run(demo_basic_crawl(save_dir="saves/demo/Demo_1", file_name="Demo-1_basic_crawl"))
	asyncio.run(demo_parallel_craw(save_dir="saves/demo/Demo_2", file_name="Demo-2_parallel_craw"))
	asyncio.run(demo_fit_markdown(save_dir="saves/demo/Demo_3", file_name="Demo-3_fit_markdown"))
	asyncio.run(demo_media_and_links(save_dir="saves/demo/Demo_4", file_name="Demo-4_media_and_links"))
	
