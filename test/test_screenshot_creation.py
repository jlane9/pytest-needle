import os


def test_screenshot(needle):
    SCREENSHOT_NAME = 'screenshot_without_baseline'
    needle.driver.get('https://www.example.com')
    try:
        needle.assert_screenshot(SCREENSHOT_NAME)
    except IOError as er:
        pass
    assert os.path.isfile(
        os.path.join(needle.options['output_dir'], SCREENSHOT_NAME+".png")), \
        "Fresh screenshot was not created (there is no baseline image)"
