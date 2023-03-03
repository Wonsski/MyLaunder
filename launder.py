from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import os
import argparse


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    STATUS = '\033[92m'
    UPDATE = '\033[93m'
    GRAY = '\33[90m'
    ENDC = '\033[0m'

class XMRWallet:
    def __init__(self, logfile=f"logs/launder_logs_{int(time.time())}.log", create_wallet=True,headless=False):
        self.address = ""
        self.mnemonic_phrase = ""
        self.xmr_balance = ""
        self.logfile = logfile
        self.url = "https://wallet.mymonero.com/"
        self.headless = headless
        self.options = webdriver.FirefoxOptions()

        if(headless):
            self.options.add_argument('--headless')
            self.options.add_argument("--width=1920")
            self.options.add_argument("--height=1080")

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

        print(f"{Colors.STATUS}[INFO]{Colors.ENDC} {Colors.OKCYAN}[{hour}:{minute}:{second}]{Colors.ENDC} {message}")

    def _createWallet(self):
        self._printStatus(f"Creating new XMR wallet...")
        
        driver = webdriver.Firefox(options=self.options)
        wait = WebDriverWait(driver, 120)

        driver.get(self.url)
        time.sleep(3)
        
        #Create new wallet option
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/a[2]")))
        time.sleep(0.5)
        elem.click()
        time.sleep(1)

        #Accept instruction
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[2]/div/div[3]/div[2]/div/div[3]/a")))
        time.sleep(0.5)
        elem.click()
        time.sleep(1)

        #Go next
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[2]/div/div[3]/div[1]/div[3]/div")))
        time.sleep(0.5)
        elem.click()
        time.sleep(1)


        #Mnemonic phrase
        mnemonic_phrase_webelem = wait.until(EC.presence_of_element_located((By.CLASS_NAME,"mnemonic-container")))

        self.mnemonic_phrase = mnemonic_phrase_webelem.text

        mnemonic_phrase_list = self.mnemonic_phrase.split()
     
        #Go next
        time.sleep(5) #page delay for mnemonic phrase save
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[2]/div/div[3]/div[1]/div[3]/div")))
        time.sleep(0.5)
        elem.click()
        time.sleep(1)

        #Verify mnemonic phrase
        word_puzzles = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"mnemonic-pill")))
        time.sleep(2)

        for i in range(len(word_puzzles)):
            word = mnemonic_phrase_list[i]

            for puzzle in word_puzzles:
                if(word.upper()==puzzle.text):
                    puzzle.click()
                    time.sleep(0.1)
                    break
        
        time.sleep(1)

        #Finish
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[2]/div/div[3]/div[1]/div[3]/div")))
        time.sleep(0.5)
        elem.click()
        time.sleep(1)

        #Access Wallet
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]")))
        time.sleep(0.5)
        elem.click()
        time.sleep(2)
        
        elem=wait.until(EC.presence_of_element_located((By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]/div/span[2]")))
        self.address = elem.text
        elem=wait.until(EC.presence_of_element_located((By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/span[2]")))
        self.xmr_balance = elem.text

        self._printStatus(f"Created wallet {Colors.GRAY}(xmr_address: {self.address})\n(Saved mnemonic in {self.logfile}){Colors.ENDC}")

        time.sleep(1)

        #Save logs
        self._saveToLogFile(f"""
        [WALLET CREATION][{datetime.now()}]
        Address: {self.address}
        Mnemonic phrase: {self.mnemonic_phrase}
        Balance: {self.xmr_balance}
        """)

        driver.close()

    def _accessWallet(self, driver):

        self._printStatus(f"Accessing wallet... {Colors.GRAY}({self.address}){Colors.ENDC}")
        
        driver.get(self.url)
        time.sleep(3)
        wait = WebDriverWait(driver, 120)
        
         #Create new wallet option
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/a[1]")))
        elem.click()
        time.sleep(1)

        #Textarea
        textarea = wait.until(EC.presence_of_element_located((By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[2]/div/div[2]/div[1]/textarea")))
        textarea.clear()
        textarea.send_keys(self.mnemonic_phrase)
        time.sleep(3)

        #Finish
        elem = wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div[1]/div[3]/div")))
        time.sleep(1)
        elem.click()
        time.sleep(1)

        #Access Wallet
        elem = wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]")))
        time.sleep(1)
        driver.execute_script("arguments[0].click();", elem)
        time.sleep(7)

    def updateWalletBalance(self):

        driver = webdriver.Firefox(options=self.options)
        self._accessWallet(driver)
        wait = WebDriverWait(driver, 120)

        self._printStatus(f"Updating wallet balance {Colors.GRAY}({self.address}){Colors.ENDC}")

        time.sleep(4)

        try:
            elem = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="stack-view-stage-view"]/div/div[1]/span[1]')))
            self.xmr_balance = elem.text
        except:
            elem = wait.until(EC.presence_of_element_located((By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[1]/span[2]")))
            self.xmr_balance = elem.text

        time.sleep(4)

        elem = wait.until(EC.presence_of_element_located((By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/span")))
        pending = elem.text
        if("pending" in pending):
            self.xmr_balance=0
            self._printStatus(f"{Colors.UPDATE}XMR is pending ({pending}){Colors.ENDC}")

        #Save logs
        self._saveToLogFile(f"""
        [WALLET BALANCE STATUS][{datetime.now()}]
        Address: {self.address}
        Balance: {self.xmr_balance}
        """)

        driver.close()

    def sendXMR(self,destination_address):


        self._saveToLogFile(f"""
        [WALLET PAYMENT REQUEST][{datetime.now()}]
        From: {self.address}
        To: {destination_address}
        """)

        driver = webdriver.Firefox(options=self.options)
        wait = WebDriverWait(driver, 120)
        self._accessWallet(driver)

        self._printStatus(f"Sending XMR\n - from: {self.address}\n - to: {destination_address}")

        #Go to send page
        time.sleep(1)
        elem = wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div/div[1]/div[1]/a[2]")))
        time.sleep(2)
        elem.click()
        time.sleep(1)
        
        #Click max
        elem = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="stack-view-stage-view"]/div/div[2]/table/tr/td/div/a')))
        time.sleep(0.5)
        elem.click()
        time.sleep(1)

        #Enter address
        elem = wait.until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/input")))
        elem.send_keys(destination_address)

        time.sleep(2)

        elem = wait.until(EC.presence_of_element_located((By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/table/tr/td/div/input")))
        time.sleep(0.5)
        transaction_value = elem.get_attribute('value')

        time.sleep(2)

        #Send XMR
        try:
            elem = wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div/div[1]/div[2]/div/div[1]/div[3]/div")))
            time.sleep(0.5)
            elem.click()

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

        self._printStatus(f"{Colors.HEADER}[TRANSACTION]{Colors.ENDC} Sent XMR\n - from: {self.address}\n - to: {destination_address}")
        time.sleep(6)
        driver.close()




if(__name__=="__main__"):
    os.system('cls' if os.name == 'nt' else 'clear')

    parser = argparse.ArgumentParser(
                    prog = 'MyMonero Launder',
                    description = 'Selenium based python script to auto-generate new XMR wallets and transfer crypto between them',
                    epilog = 'Author: Radoslaw Rajda')
    
    parser.add_argument('destinationWallet', help='The last wallet where XMR will be sent')
    parser.add_argument('walletAmount', help='Amount of wallets to generate',type=int) 
    parser.add_argument('-delay', help='How often to refresh your wallet account balance? (Default 300 seconds)',default=300) 
    parser.add_argument('--mnemonic',dest='startFromExistingWallet', help='Use existing XMR starting wallet',action='store_true') 
    parser.add_argument('--headless',dest='headlessMode', help='Run selenium in headless mode',action='store_true') 

    args = parser.parse_args()

    logfile=f"logs/launder_logs_{int(time.time())}.log"

    if(args.headlessMode):
            print(f"{Colors.UPDATE}Running in headless mode{Colors.ENDC}")

    if(args.startFromExistingWallet):
        mnemonic = input("Input mnemonic phrase: ")
        os.system('cls' if os.name == 'nt' else 'clear')

        wallet = XMRWallet(logfile=logfile, create_wallet=False, headless=args.headlessMode)
        wallet.mnemonic_phrase = mnemonic
        wallet.address = "User address"
    else:
        wallet = XMRWallet(logfile=logfile, headless=args.headlessMode)

        delay=args.delay

        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\nSend XMR to address: {wallet.address}\n\n")
        print(f"[*] Payment delay: {delay} seconds")
        
        while True:
            time.sleep(delay)
            wallet.updateWalletBalance()

            if float(wallet.xmr_balance)>0:
                print(f"{Colors.STATUS}XMR received at {datetime.now()}{Colors.ENDC}")
                break

    for i in range(args.walletAmount):

        print(f"{Colors.HEADER}[NEW WALLET]{Colors.ENDC} [{Colors.OKBLUE}Num: {i+1}{Colors.ENDC}]")
        next_wallet = XMRWallet(logfile=logfile,headless=args.headlessMode)

        wallet.sendXMR(next_wallet.address)

        print(f"{Colors.STATUS}[INFO]{Colors.ENDC} Waiting for XMR to receive ({args.delay} seconds refresh)")

        while True:
            time.sleep(args.delay)
            next_wallet.updateWalletBalance()

            if float(next_wallet.xmr_balance)>0:
                print(f"{Colors.STATUS}XMR received at {datetime.now()}{Colors.ENDC}")
                break
        
        wallet = next_wallet


    wallet.sendXMR(args.destinationWallet)