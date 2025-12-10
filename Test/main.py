import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

@pytest.fixture(scope="class")
def setup(request):
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    request.cls.driver = driver
    request.cls.base_url = "http://127.0.0.1:5000/"
    
    try:
        driver.get(request.cls.base_url)
        time.sleep(1)  # Allow page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Sign Up")))
    except Exception as e:
        print(f"Failed to load URL: {request.cls.base_url}")
        print(f"Error: {e}")
        driver.quit()
        raise
    
    yield
    driver.quit()

@pytest.mark.usefixtures("setup")
class TestUserActions:
    login_user_email = 'TEST@MAIL.COM'
    login_user_password = 'test@123'    
    new_user_email = 'prz@test.com'
    new_user_password = 'prz@123'

    @pytest.mark.signup
    def test_empty_registration_form_submission(self):
        self.driver.find_element(By.LINK_TEXT, 'Sign Up').click()
        self.driver.find_element(By.XPATH, '//input[@type="submit" and @value="Sign up"]').click()
        validation_message = self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#email').get_attribute("validationMessage")
        assert validation_message == "Please fill out this field."

    @pytest.mark.signup
    def test_invalid_email_format(self):
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#email').send_keys('prz_test')
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#password').send_keys('prz@123')
        self.driver.find_element(By.XPATH, '//input[@type="submit" and @value="Sign up"]').click()
        validation_message = self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#email').get_attribute("validationMessage")
        assert validation_message == "Please include an '@' in the email address. 'prz_test' is missing an '@'."
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#email').clear()

    @pytest.mark.signup
    def test_signup_with_valid_email_no_password(self):
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#email').clear()
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#email').send_keys('prz@test.com')
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#password').clear()
        self.driver.find_element(By.XPATH, '//input[@type="submit" and @value="Sign up"]').click()
        validation_message = self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#password').get_attribute("validationMessage")
        assert validation_message == "Please fill out this field."

    @pytest.mark.signup
    def test_valid_registration(self):
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#email').clear()
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#email').send_keys(self.new_user_email)
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#password').clear()
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#password').send_keys(self.new_user_password)
        self.driver.find_element(By.XPATH, '//input[@type="submit" and @value="Sign up"]').click()
        time.sleep(1)
        body_text = self.driver.find_element(By.TAG_NAME, 'body').text
        assert "User signed up successfully!" in body_text

    @pytest.mark.signup
    def test_duplicate_registration(self):
        self.driver.get(self.base_url)
        self.driver.find_element(By.LINK_TEXT, 'Sign Up').click()
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#email').send_keys(self.new_user_email)
        self.driver.find_element(By.CSS_SELECTOR, '#signupModal input#password').send_keys(self.new_user_password)
        self.driver.find_element(By.XPATH, '//input[@type="submit" and @value="Sign up"]').click()
        time.sleep(1)
        body_text = self.driver.find_element(By.TAG_NAME, 'body').text
        assert "User with that email already exists." in body_text

    @pytest.mark.login
    def test_empty_login_form_submission(self):
        self.driver.get(self.base_url)
        self.driver.find_element(By.XPATH, '//input[@type="submit" and @value="login"]').click()
        email_validation_message = self.driver.find_element(By.ID, 'email').get_attribute("validationMessage")
        assert email_validation_message == "Please fill out this field."
        self.driver.find_element(By.ID, 'email').send_keys('test@qa.com')
        self.driver.find_element(By.XPATH, '//input[@type="submit" and @value="login"]').click()
        password_validation_message = self.driver.find_element(By.ID, 'password').get_attribute("validationMessage")
        assert password_validation_message == "Please fill out this field."
        self.driver.find_element(By.ID, 'email').clear()

    @pytest.mark.login
    def test_login_with_wrong_username_password(self):
        self.driver.find_element(By.ID, 'email').send_keys('test@qa.com')
        self.driver.find_element(By.ID, 'password').send_keys('test')
        self.driver.find_element(By.XPATH, '//input[@type="submit" and @value="login"]').click()
        time.sleep(1)
        body_text = self.driver.find_element(By.TAG_NAME, 'body').text
        assert "invalid credentials" in body_text

    @pytest.mark.login
    def test_login_with_wrong_password(self):
        self.driver.get(self.base_url)
        self.driver.find_element(By.ID, 'email').send_keys(self.login_user_email)
        self.driver.find_element(By.ID, 'password').send_keys('test')
        self.driver.find_element(By.XPATH, '//input[@type="submit" and @value="login"]').click()
        time.sleep(1)
        body_text = self.driver.find_element(By.TAG_NAME, 'body').text
        assert "invalid credentials." in body_text

    @pytest.mark.login
    def test_valid_user_login(self):
        self.driver.get(self.base_url)
        self.driver.find_element(By.ID, 'email').send_keys(self.login_user_email)
        self.driver.find_element(By.ID, 'password').send_keys(self.login_user_password)
        self.driver.find_element(By.XPATH, '//input[@type="submit" and @value="login"]').click()
        time.sleep(1)
        assert "Registered Users" in self.driver.find_element(By.TAG_NAME, 'h1').text and self.driver.find_element(By.TAG_NAME, 'table')

    @pytest.mark.user
    def test_check_for_unique_user_id(self):
        user_ids = [row.find_elements(By.TAG_NAME, 'td')[0].text.strip() for row in self.driver.find_elements(By.XPATH, '//table/tbody/tr') if row.find_elements(By.TAG_NAME, 'td')[1].text.strip().lower() == self.new_user_email]
        print(f"The ID for '{self.new_user_email}' is unique: {user_ids[0]}" if len(user_ids) == 1 else f"The ID for '{self.new_user_email}' is not unique. It appears {len(user_ids)} times." if len(user_ids) > 1 else f"No entry found for the email '{self.new_user_email}'.")

    @pytest.mark.user
    def test_delete_a_user(self):
        self.driver.find_element(By.XPATH, f"//tr[td/text()='{self.new_user_email}']//button[contains(@class, 'delete-button')]").click()
        self.driver.refresh()
        deleted_row = self.driver.find_elements(By.XPATH, f"//tr[td/text()='{self.new_user_email}']")
        assert len(deleted_row) == 0

    @pytest.mark.logout
    def test_logout_access_target_page_without_logging_in(self):
        self.driver.find_element(By.LINK_TEXT, 'Log out').click()
        self.driver.get(self.base_url + 'users')
        assert "Login or Sign Up" in self.driver.title