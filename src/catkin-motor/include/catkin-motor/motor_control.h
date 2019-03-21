#define DigitalOut mode0(PTB0);
#define DigitalOut mode0(PTB0);
#define DigitalOut mode0(PTB0);

/*Shoulder motor parameters*/
#define shoulder PTA1; //Step, toggle to run
#define dir1 PTA2; 

void move(DigitalOut motor, int speed, int duration){
    int i;
    for (i=0; i<=duration; i++){
        motor ^= 0;
    }
}
