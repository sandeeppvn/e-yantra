 
/*
 * Team Id: 1146
 * Author List: Shraddha B.L.S, Sonicka R, Sandeep PVN, Sneha J Pillai
 * Filename: final.c
 * Theme: Cross a Creater
 * Functions: buzzer_pin_config (),motion_pin_config (), main(),servo_init(),port_init(),timer_init(),servo(),buzzer_on(),buzzer_off(),uart0_init(),ISR(),init_devices()
 * Global Variables: data
 */ 

#define F_CPU 14745600
#include<avr/io.h>
#include<avr/interrupt.h>
#include<util/delay.h>

unsigned char data; //to store received data from UDR1
// unsigned int motor1DutyCycle = 100 // % of power given to the motor1
//unsigned int motor2DutyCycle = (int)(100*(1 - sin(0.139626))); // % of power given to the motor2
/*
 * Function Name: buzzer_pin_config
 * Input: NONE
 * Output:NONE
 * Logic:The pins/ports where the buzzer is connected are enabled.
 * initially the default value is that the buzzer is off
 * Example Call:buzzer_pin_config()
 */

void buzzer_pin_config (void)
{
	DDRC = DDRC | 0x08;		//Setting PORTC 3 as output//data direction register
	PORTC = PORTC & 0xF7;		//Setting PORTC 3 logic low to turnoff buzzer
}
/*
 * Function Name: motion_pin_config
 * Input: NONE
 * Output:NONE
 * Logic:The pins/ports where the DC motors are connected(port A,pins 0,1,2and3) are enabled.
 * initially the default value is that the buzzer is off
 * Example Call:buzzer_pin_config()
 */

void motion_pin_config (void)
{
	DDRA = DDRA | 0x0F;      //Port A(pin 1,2,3 and 4) is set as Output ports
	PORTA = PORTA & 0xF0;    //Setting the lower pins(1,2,3 and 4) to stop initially and other pins of port as is.
	//enable the motor driver IC(L293D) using PORT L
	DDRL = DDRL | 0x18;   //Setting PL3 and PL4 pins as output for PWM generation
	PORTL = PORTL & ~(0x18); //PL3 and PL4 pins are for velocity control using PWM.
}
/*
 * Function Name: servo_init()
 * Input: NONE
 * Output:NONE
 * Logic:The pins/ports where the servo motor are connected(port B) are enabled.(pin 5, without disturbing other values therefore or operation.)
 * Example Call:servo_init()
 */
void servo_init()
{
	
	DDRB=DDRB |0X20;
	PORTB=PORTB|0X20;
}

/*
 * Function Name: port_init()
 * Input: NONE
 * Output:NONE
 * Logic:Function to initialize ports
 * Example Call:port_init()
 */
void port_init()
{
	motion_pin_config();//calls funtion for dc motor initialization.
	buzzer_pin_config();//calls funtion for buzzer initialization.
}
/*
 * Function Name: timer_init()
 * Input: NONE
 * Output:NONE
 * Logic:Function to initialize timer for servo.
 * Example Call:timer_init()
 */

void timer_init()
{
	
	TCCR1A=0x00;//Timer Contol Counter Register
	ICR1=1023;
	//TCNT1H=0xFC;
	//TCNT1L=0x01;
	TCNT1=0xFC01;
	OCR1A=1023;//output compare Register
	TCCR1A=0XAB;
	TCCR1B=0x0C;
}
/*
 * Function Name: pwmTimer5_Init()
 * Input: NONE
 * Output:NONE
 * Logic:Function to initialize timer for DC motor to perform PWM due to misalignment of the DC motors.
 * Example Call:pwmTimer5_Init()
 */
void pwmTimer5_Init(void)
{
	TCCR5A = (1 << WGM50)|(1 << COM5A1)|(1 << COM5B1);
	TCCR5B = (1 << WGM52);
	OCR5B = 255; //Trigger threshold right
	OCR5A = 250; //Trigger threshold left
	TIMSK5 = 0x01;
	TCCR5B = (1 << CS51); // Start timer with a prescaler of 8
}	
/*
 * Function Name: servo()
 * Input: degrees we want servo to rotate
 * Output:servo will rotate
 * Logic:sets a value into Output compare register assigned to its specific register such that the time can determine the angle.
 * Example Call:servo(180)
 */

void servo(unsigned char degrees)
{
	float regval=((float)degrees*0.512)+34.56;
	OCR1A=(uint16_t)regval;
}
/*
 * Function Name: buzzer_on()
 * Input:NONE
 * Output:buzzer will turn on
 * Logic:The buzzer starts buzzing once the PINC's pin 3 becomes high
 * Example Call:buzzer_on()
 */
void buzzer_on (void)
{
unsigned char port_restore = 0;
port_restore = PINC;	//to read from port
port_restore = port_restore | 0x08;
PORTC = port_restore;
}
/*
 * Function Name: buzzer_off()
 * Input:NONE
 * Output:buzzer will turn on
 * Logic:The buzzer stops buzzing once the PINC's pins are negated.
 * Example Call:buzzer_off()
 */

void buzzer_off (void)
{
	unsigned char port_restore = 0;
	port_restore = PINC;
	port_restore = port_restore & 0xF7;
	PORTC = port_restore;
}
/*
 * Function Name:uart0_init()
 * Input:NONE
 * Output:Serial Communication will be established.
 * Logic:The necessary pins are set high and the baud rate is set for the Xbee to communicate serially with the other Xbee(receiver) module mounted on the bot.
 * Example Call:uart0_init()
 */
void uart0_init(void)
{
	UCSR0B = 0x00; //disable while setting baud rate
	UCSR0A = 0x00;
	UCSR0C = 0x06;
	UBRR0L = 0x5F; //set baud rate lo
	UBRR0H = 0x00; //set baud rate hi
	UCSR0B = 0x98;
}
/*
 * Function Name:ISR(USART0_RX_vect)
 * Input:serial data from Xbee on UDR0
 * Output:Bot operation based on values received.
 * Logic:The Xbee on the bot receives the data and stores it in UDR0 if any of the values listed below are received the the respective bot functions are performed 
 * if the Xbee receives data it enters this Interrupt Service routine 
 * Example Call:calls by self when interrupt occurs.
 */


ISR(USART0_RX_vect)	// ISR for receive complete interrupt
{
	data = UDR0; 				//making copy of data from UDR0 in 'data' variable

	UDR0 = data; 				//echo data back to PC
if(data == 0x31) //ASCII value of 1
{
	servo(180); //pick
}
if(data == 0x30) //ASCII value of 0
{
	servo(0); //pick
}

if(data == 0x38) //ASCII value of 8
{
	PORTA=0x06;  //forward
}

if(data == 0x32) //ASCII value of 2
{
	PORTA=0x09; //back
}

if(data == 0x34) //ASCII value of 4
{
	PORTA=0x05;  //left
}

if(data == 0x36) //ASCII value of 6
{
	PORTA=0x0A; //right
}

if(data == 0x35) //ASCII value of 5
{
	PORTA=0x00; //stop
}

if(data == 0x37) //ASCII value of 7
{
	buzzer_on();
}

if(data == 0x39) //ASCII value of 9
{
	buzzer_off();
}

}
/*
 * Function Name: init_devices()
 * Input: NONE
 * Output:NONE
 * Logic: initializes the respective ports for the respective device calls.
 * Example Call: init_devices()
 */


//Function To Initialize all The Devices
void init_devices()
{
	cli(); //Clears the global interrupts
	port_init();  //Initializes all the ports
	uart0_init(); //Initialize UART1 for serial communication
	servo_init();
	timer_init();
	pwmTimer5_Init();
	sei();   //Enables the global interrupts
}
/*
 * Function Name:ISR(TIMER5_OVF_vect)
 * Input: used if required.(i.e we want to change PWM of the BOT)
 * Output:NONE
 * Logic: initializes the respective ports for the respective device calls.
 * Example Call: in built call on value of TIMER5_OVF_vect.
 */
ISR(TIMER5_OVF_vect)
{
	// If you'd want to change either motor's pwm, do it here
}

//Main Function
/*
 * Function Name:main()
 * Input: NONE
 * Output:NONE
 * Logic: calls funtion of the devices that have to be initalized which are to be used later by serial communication values. 
 * Example Call: NO call.
 */
int main(void)
{
	init_devices();
	while(1);
}
