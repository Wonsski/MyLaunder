from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import os


class XMRWallet:
    def __init__(self, logfile=f"logs/launder_logs_{int(time.time())}.log"):
        self.address = ""
        self.mnemonic_phase = ""
        self.xmr_balance = ""
        self.logfile = logfile
        self.url = "https://wallet.mymonero.com/"

        self._createWallet()

    def _saveToLogFile(self,message):
        os.makedirs(os.path.dirname(self.logfile), exist_ok=True)

        with open(self.logfile,'a') as f:
            f.write(message.replace('   ',''))

    def _createWallet(self):
        print("[*] Creating new XMR wallet...")
        
        driver = webdriver.Firefox()

        driver.get(self.url)
        time.sleep(3)
        
        #Create new wallet option
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/a[2]").click()

        #Accept instruction
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[2]/div/div[3]/a").click()

        #Go next
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[1]/div[3]/div").click()

        #Mnemonic phase
        mnemonic_phase_webelem = driver.find_element(By.CLASS_NAME,"mnemonic-container")

        self.mnemonic_phase = mnemonic_phase_webelem.text

        mnemonic_phase_list = self.mnemonic_phase.split()
        time.sleep(3)
        
        #Go next
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[1]/div[3]/div").click()

        #Verify mnemonic phase
        word_puzzles = driver.find_elements(By.CLASS_NAME,"mnemonic-pill")

        for i in range(len(word_puzzles)):
            word = mnemonic_phase_list[i]

            for puzzle in word_puzzles:
                if(word.upper()==puzzle.text):
                    puzzle.click()
                    time.sleep(0.1)
                    break

        #Finish
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[1]/div[3]/div").click()
        time.sleep(2)

        #Access Wallet
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]").click()

        self.address = driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]/div/span[2]").text
        self.xmr_balance = driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/span[2]").text

        print(f"[*] Created wallet (xmr_address: {self.address})(More details in {self.logfile})")

        #Save logs
        self._saveToLogFile(f"""
        [WALLET CREATION][{datetime.now()}]
        Address: {self.address}
        Mnemonic phase: {self.mnemonic_phase}
        Balance: {self.xmr_balance}
        """)

        driver.close()

    def _accessWallet(self, driver):
        
        driver.get(self.url)
        time.sleep(3)
        
         #Create new wallet option
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/a[1]").click()

        #Textarea
        textarea = driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[2]/div/div[2]/div[1]/textarea")
        textarea.clear()
        textarea.send_keys(self.mnemonic_phase)
        time.sleep(1)

        #Finish
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[1]/div[3]/div").click()
        time.sleep(2)



    def updateWalletBalance(self):
        
        print(f"[*] Updating wallet balance ({self.address})")

        driver = webdriver.Firefox()
        self._accessWallet(driver)

        #Access Wallet
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]").click()

        self.xmr_balance = driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/span[2]").text

        #Save logs
        self._saveToLogFile(f"""
        [WALLET BALANCE STATUS][{datetime.now()}]
        Address: {self.address}
        Balance: {self.xmr_balance}
        """)

        driver.close()

    #TODO
    def sendXMR(self,destination_address):
        pass


a = XMRWallet()
a.updateWalletBalance()