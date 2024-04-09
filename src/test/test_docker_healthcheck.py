import app
import uvicorn
import pytest
import config
import asyncio
import multiprocessing

from docker_healthcheck import check_health


class TestApp:
    """Test the app class."""

    async def start(self):
        print("Starting app")
        """ Bring server up. """
        self.proc = multiprocessing.Process(
            target=uvicorn.run,
            args=(app.app,),
            kwargs={"host": config.HOST, "port": int(config.PORT), "log_level": "info"},
            daemon=True,
        )

        await self.proc.start()

    async def terminate(self):
        """Shutdown the app."""
        self.proc.terminate()


@pytest.fixture
async def test_webserver():
    """Setup the test app."""
    web = TestApp()
    await web.start()
    yield web
    await web.terminate()


@pytest.mark.asyncio
async def test_check_health(test_webserver):
    await asyncio.sleep(1)
    assert not check_health()
