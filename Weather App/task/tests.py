from hstest import FlaskTest, CheckResult, WrongAnswer
from hstest import dynamic_test
from hstest.dynamic.security.exit_handler import ExitHandler

import asyncio
from pyppeteer import launch


class FlaskProjectTest(FlaskTest):
    source = 'web.app'

    async def test_main_page_structure(self):
        browser = await launch()
        page = await browser.newPage()

        await page.goto(self.get_url())
        html_code = await page.content()

        if "Hello, world!" not in html_code:
            raise WrongAnswer("'/' route should return 'Hello, world!' message!")

        await browser.close()

    @dynamic_test()
    def test(self):
        ExitHandler.revert_exit()
        asyncio.get_event_loop().run_until_complete(self.test_main_page_structure())
        return CheckResult.correct()


if __name__ == '__main__':
    FlaskProjectTest().run_tests()
