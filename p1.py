# Import libraries
import time 
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
 
# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
GPIO.setmode(GPIO.BOARD)
# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
DC1 = 0
DC2 =0
n_guess=0
buzzer = None
eeprom = ES2EEPROMUtils.ES2EEPROM()
user_guess=0

rnum=2 # set it up in the main function

# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")
    

# Print the game menu
def menu():
    global end_of_game
    global user_guess
    global rnum
    #testing eeprom
    
        
    
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        #print(GPIO.input(15))
        user_guess=0
        rnum = generate_number()
       # print(rnum)
        value= rnum
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    for i  in range(3):
              x=raw_data[i]
              
              print("%d-%s took %d guesses"%(i+1,x[0],x[1]))
    # print out the scores in the required format
    menu()


# Setup Pins
def setup():
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(11, GPIO.OUT)
    
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.output(11, GPIO.LOW)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(15, GPIO.LOW)
    
    # Setup PWM channels
   
    GPIO.setup(32, GPIO.OUT)
    GPIO.setup(33, GPIO.OUT)
    global myled
    global myBuz 
    myled = GPIO.PWM(32,100)
    myBuz = GPIO.PWM(33,100)
    myled.start(0)
    myBuz.start(0)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(16, GPIO.FALLING, callback=my_callback1, bouncetime=200)
    GPIO.add_event_detect(18, GPIO.FALLING, callback=my_callback2, bouncetime=200)


# Load high scores
def my_callback1(channel):

    tm=time.time()
    while GPIO.input(channel)==0:
          pass
    stt=time.time()-tm
    if stt>=0.1:
          #print("pressed ch1") 
          btn_increase_pressed()
def my_callback2(channel):
    global bs
    global user_guess
    
    stime=time.time()
    while GPIO.input(channel)==0:
          pass
    bt=time.time()-stime
    if bt<=0.1:
         bs=1
    elif bt<=1:
         #print("pressed ch2")
         btn_guess_pressed()
    else:
         bs=3
         GPIO.output(11, GPIO.LOW)
         GPIO.output(13, GPIO.LOW)
         GPIO.output(15, GPIO.LOW)
         
         menu()

def fetch_scores():
    # get however many scores there are
    score_count = 0
    ndata=eeprom.read_block(0,4)
    #print(ndata[0])
    rd= eeprom.read_block(0,ndata[0]*4+4)
    #print(rd)
    scores=[]
    i=0
    while True:
          f=[]
          wd=(chr(rd[i])+chr(rd[i+1])+chr(rd[i+2]))

          f.append(wd)
          f.append(rd[i+3])
          if i+4>=len(rd):
              break
          if  rd[i+4]==0 and  f[1]==0 :
              break
          elif f[1]!=0 :
              score_count+=1
              scores.append(f)
          i+=4

    # Get the scores
    score_count = ndata[0]
    # convert the codes back to ascii
    #print(scores)
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    global myBuz
    global myled
    s_count, ss = fetch_scores() 
    GPIO.output(11, GPIO.LOW)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(15, GPIO.LOW)
    myled.ChangeDutyCycle(0)
    myBuz.ChangeDutyCycle(0)
    name=input("Enter 3 letter name: ")
    while True:
          if len(name)!=3:
                 name=input("Invalid Name entry. Please enter a 3 letter name: ")
          else:
                 break
    eeprom.clear(2048)
    eeprom.write_block(0, [s_count+1])
    ws=""
    tb=0
    for char in name:
             if tb>=3:
                break
             else:
                tb+=1
                ws=ws+char
    #print("here")
    #print([ws]+[user_guess])
    ss.append([ws]+[user_guess])
    ss.sort(key=lambda x: x[1])
    #print(ss)
    #print("sorted list")
    for i, sc in enumerate(ss):
              dwrite=[]
              #print(sc[0])
              #print(i)
              # print(sc)
              # print("list data")
              if isinstance(sc[0], int):
                 continue
              for char in sc[0]:
                      dwrite.append(ord(char))
              dwrite.append(sc[1])
              eeprom.write_block(i+1,dwrite)
    # include new score
    # sort
    # update total amount of scores
    # write new scores
    


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed():
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    if GPIO.input(15) == 0:
        if GPIO.input(13)== 0:
            if GPIO.input(11)== 0:
                GPIO.output(11, GPIO.HIGH)
            else:
                GPIO.output(11, GPIO.LOW)
                GPIO.output(13, GPIO.HIGH)
        else:
            if GPIO.input(11)==0:
                GPIO.output(11, GPIO.HIGH)
            else:
                GPIO.output(11, GPIO.LOW)
                GPIO.output(13, GPIO.LOW)
                GPIO.output(15, GPIO.HIGH)
    elif GPIO.input(11) == 1 and GPIO.input(13) == 1 and GPIO.input(15) == 1  :
         GPIO.output(11, GPIO.LOW)
         GPIO.output(13, GPIO.LOW)
         GPIO.output(15, GPIO.LOW)
    else:
        if GPIO.input(13)==0:
            if GPIO.input(11)==0:
                GPIO.output(11, GPIO.HIGH)
            else:
                GPIO.output(11, GPIO.LOW)
                GPIO.output(13, GPIO.HIGH)
        else:
            if GPIO.input(11)==0:
                GPIO.output(11, GPIO.HIGH)
            else:
                GPIO.output(11, GPIO.LOW)
                GPIO.output(13, GPIO.LOW)
                GPIO.output(15, GPIO.HIGH)
                     
    


# Guess button
def btn_guess_pressed():
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    global user_guess
    global n_guess
    user_guess+=1
    if user_guess>=8:
       print("Sorry.... Game over")
       menu()
    #converts led count to number  
    n_guess=0;
    if GPIO.input(11)==1:
        n_guess+=1
    if GPIO.input(13)==1:
        n_guess+=2
    if GPIO.input(15)==1:
        n_guess+=4
    # Compare the actual value with the user value displayed on the LEDs   
    if n_guess==rnum:
         
         print("You must be psychic")
         save_scores()
         menu()
    else:
        accuracy_leds()
        trigger_buzzer()
    
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
   


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    #print("userg= %d rnum= %d"%(n_guess,rnum))
    if n_guess>rnum:
        #print("changeledb")
        brightness=100*(8-n_guess)/(8-rnum)
    else:
        #print("changeledb")
        brightness= 100*(n_guess/rnum)
      
    myled.ChangeDutyCycle(brightness)
    
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    myBuz.ChangeDutyCycle(50)
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    if abs(rnum-n_guess)>=3:
        
        myBuz.ChangeFrequency(1)
    
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    if abs(rnum-n_guess)==2:
        #print("chang2buz =%d"%(n_guess))
        myBuz.ChangeFrequency(2)
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    if abs(rnum-n_guess)==1:
        #print("chang3buz =%d"%(n_guess))
        myBuz.ChangeFrequency(40)
    


if __name__ == "__main__":
    try:
        # Call setup function
        
        setup()
        
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()