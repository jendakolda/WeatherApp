from hstest import FlaskTest, CheckResult, WrongAnswer
from hstest import dynamic_test
from hstest.dynamic.security.exit_handler import ExitHandler

import asyncio
from pyppeteer import launch


class FlaskProjectTest(FlaskTest):
    source = 'web.app'

    @classmethod
    async def check_cards_in_the_page(cls, page, cards_number):
        cards = await page.querySelectorAll('div.card')

        if len(cards) == 0:
            raise WrongAnswer("Can't find <div> blocks with class 'card'")

        if len(cards) != cards_number:
            raise WrongAnswer(f"Found {len(cards)} <div> blocks with class 'card', but should be {cards_number}!")

        for card in cards:
            degrees = await card.querySelector('div.degrees')
            if degrees is None:
                raise WrongAnswer(
                    "One of the <div> blocks with card class 'card' doesn't contain <div> block with class 'degrees'")
            state = await card.querySelector('div.state')
            if state is None:
                raise WrongAnswer(
                    "One of the <div> blocks with card class 'card' doesn't contain <div> block with class 'state'")
            city = await card.querySelector('div.city')
            if city is None:
                raise WrongAnswer(
                    "One of the <div> blocks with card class 'card' doesn't contain <div> block with class 'city'")

    async def test_response_async(self):
        browser = await launch()
        page = await browser.newPage()
        try:
            await page.goto(self.get_url())
        except Exception:
            raise WrongAnswer(f"Can't access the main page with URL '{self.get_url()}'")
        await browser.close()

    @dynamic_test(order=1)
    def test_response(self):
        ExitHandler.revert_exit()
        asyncio.get_event_loop().run_until_complete(self.test_response_async())
        return CheckResult.correct()

    async def test_main_page_structure_async(self):
        browser = await launch()
        page = await browser.newPage()

        await page.goto(self.get_url())

        cards_div = await page.querySelector('div.cards')

        if cards_div is None:
            raise WrongAnswer("Can't find <div> block with class 'cards'")

        button = await page.querySelector('button.submit-button')

        if button is None:
            raise WrongAnswer("Can't find a button with 'submit-button' class!")

        input_field = await page.querySelector('input#input-city')

        if input_field is None:
            raise WrongAnswer("Can't find input field with 'input-city' id!")

        await self.check_cards_in_the_page(page, 3)

        await browser.close()

        return CheckResult.correct()

    @dynamic_test(order=2)
    def test_main_page_structure(self):
        asyncio.get_event_loop().run_until_complete(self.test_main_page_structure_async())
        return CheckResult.correct()

    async def test_add_city_async(self):
        browser = await launch()
        page = await browser.newPage()
        await page.goto(self.get_url())

        input_field = await page.querySelector('input#input-city')
        await input_field.type('Boston')

        button = await page.querySelector('button.submit-button')

        await asyncio.gather(
            page.waitForNavigation(),
            button.click(),
        )

        cards_div = await page.querySelector('div.cards')

        if cards_div is None:
            raise WrongAnswer("Can't find <div> block with class 'cards'")

        await self.check_cards_in_the_page(page, 4)

    @dynamic_test(order=3)
    def test_add_city(self):
        asyncio.get_event_loop().run_until_complete(self.test_add_city_async())
        return CheckResult.correct()


if __name__ == '__main__':
    FlaskProjectTest().run_tests()
