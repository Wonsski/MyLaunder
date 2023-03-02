from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import os


class XMRWallet:
    def __init__(self, logfile=f"logs/launder_logs_{int(time.time())}.log", create_wallet=True):
        self.address = ""
        self.mnemonic_phrase = ""
        self.xmr_balance = ""
        self.logfile = logfile
        self.url = "https://wallet.mymonero.com/"

        if(create_wallet):
            self._createWallet()

    def _saveToLogFile(self,message):
        os.makedirs(os.path.dirname(self.logfile), exist_ok=True)

        with open(self.logfile,'a') as f:
            f.write(message.replace('   ',''))

    def _printStatus(self,message):

        hour = datetime.now().hour
        minute = datetime.now().minute
        second = datetime.now().second

        if hour<10: 
            hour='0'+str(hour)
        if minute<10: 
            minute='0'+str(minute)
        if second<10: 
            second='0'+str(second)

        print(f"[*][{hour}:{minute}:{second}] {message}")

    def _createWallet(self):
        self._printStatus("Creating new XMR wallet...")
        
        driver = webdriver.Firefox()

        driver.get(self.url)
        time.sleep(3)
        
        #Create new wallet option
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/a[2]").click()

        #Accept instruction
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[2]/div/div[3]/a").click()

        #Go next
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[1]/div[3]/div").click()

        #Mnemonic phrase
        mnemonic_phrase_webelem = driver.find_element(By.CLASS_NAME,"mnemonic-container")

        self.mnemonic_phrase = mnemonic_phrase_webelem.text

        mnemonic_phrase_list = self.mnemonic_phrase.split()
        time.sleep(3)
        
        #Go next
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[1]/div[3]/div").click()

        #Verify mnemonic phrase
        word_puzzles = driver.find_elements(By.CLASS_NAME,"mnemonic-pill")

        for i in range(len(word_puzzles)):
            word = mnemonic_phrase_list[i]

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
        time.sleep(2)

        self.address = driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]/div/span[2]").text
        self.xmr_balance = driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/span[2]").text

        self._printStatus(f"Created wallet (xmr_address: {self.address})(More details in {self.logfile})")

        #Save logs
        self._saveToLogFile(f"""
        [WALLET CREATION][{datetime.now()}]
        Address: {self.address}
        Mnemonic phrase: {self.mnemonic_phrase}
        Balance: {self.xmr_balance}
        """)

        driver.close()

    def _accessWallet(self, driver):
        
        driver.get(self.url)
        time.sleep(5)
        
         #Create new wallet option
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/a[1]").click()

        #Textarea
        textarea = driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[2]/div/div[2]/div[1]/textarea")
        textarea.clear()
        textarea.send_keys(self.mnemonic_phrase)
        time.sleep(1)

        #Finish
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[1]/div[3]/div").click()
        time.sleep(2)

    def updateWalletBalance(self):
        
        self._printStatus(f"Updating wallet balance ({self.address})")

        driver = webdriver.Firefox()
        self._accessWallet(driver)

        #Access Wallet
        driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]").click()
        time.sleep(2)

        try:
            self.xmr_balance = driver.find_element(By.XPATH,'//*[@id="stack-view-stage-view"]/div/div[1]/span[1]').text
        except:
            self.xmr_balance = driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/span[2]").text

        pending = driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/span").text
        if("pending" in pending):
            self.xmr_balance=0

        #Save logs
        self._saveToLogFile(f"""
        [WALLET BALANCE STATUS][{datetime.now()}]
        Address: {self.address}
        Balance: {self.xmr_balance}
        """)

        driver.close()

    def sendXMR(self,destination_address):

        self._printStatus(f"Sending XMR\n - from: {self.address}\n - to: {destination_address}")

        self._saveToLogFile(f"""
        [WALLET PAYMENT REQUEST][{datetime.now()}]
        From: {self.address}
        To: {destination_address}
        """)

        driver = webdriver.Firefox()
        self._accessWallet(driver)

        #Go to send page
        driver.find_element(By.XPATH,'//*[@id="tabButton-send"]').click()
        
        #Click max
        driver.find_element(By.XPATH,'//*[@id="stack-view-stage-view"]/div/div[2]/table/tr/td/div/a').click()

        #Enter address
        driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/input").send_keys(destination_address)

        transaction_value = driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/table/tr/td/div/input").get_attribute('value')

        #Send XMR
        try:
            time.sleep(1)
            driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[1]/div[3]/div").click()
            self._saveToLogFile(f"""
             [WALLET PAYMENT SUCCESS][{datetime.now()}]
             From: {self.address}
             To: {destination_address}
             Amount: {transaction_value}
            """)
        except:
            print(f"[!][ERROR] Something gone wrong with XMR transaction. Details: {self.logfile}")
            self._saveToLogFile(f"""
            [WALLET PAYMENT FAILURE][{datetime.now()}]
            From: {self.address}
            To: {destination_address}
            Amount: {transaction_value}
            Wallet details:
            - Wallet_address: {self.address}
            - Mnemonic phrase: {self.mnemonic_phrase}
            - Last known XMR balance: {self.xmr_balance}
            """)

        time.sleep(5)
        driver.close()

if(__name__=="__main__"):
    destination_wallet_address = input("Input destination wallet address: ")
    wallet_amount = int(input("Input wallet amount to generate: "))

    use_existing = input("Do you wanna use existing wallet? y/n: ")

    logfile=f"logs/launder_logs_{int(time.time())}.log"

    if(use_existing=='y'):
        mnemonic = input("Input mnemonic phrase: ")

        wallet = XMRWallet(logfile=logfile, create_wallet=False)
        wallet.mnemonic_phrase = mnemonic
        delay=1
    else:
        wallet = XMRWallet(logfile=logfile)
        delay=900
    
    print("\n\n")
    print(25*'-')
    print(f"\nSend XMR to address: {wallet.address}\n")
    print(25*'-')
    print(f"[*] Payment delay: {delay} seconds")
    
    while True:
        time.sleep(delay)
        wallet.updateWalletBalance()

        if float(wallet.xmr_balance)>0:
            print(f"XMR received at {datetime.now()}")
            break
        delay=900

    for i in range(wallet_amount):
        print(f"[{i+1}] wallet")
        next_wallet = XMRWallet(logfile=logfile)

        wallet.sendXMR(next_wallet.address)

        print("[*] Waiting for XMR to receive (15min refresh)")

        while True:
            time.sleep(900)
            next_wallet.updateWalletBalance()

            if float(next_wallet.xmr_balance)>0:
                print(f"XMR received at {datetime.now()}")
                break
        
        wallet = next_wallet

    next_wallet.sendXMR(destination_wallet_address)