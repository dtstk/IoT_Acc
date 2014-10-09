

#include <unistd.h>  // sleep()
#include <pthread.h> 
#include <stdio.h>   
#include <stdlib.h>  // EXIT_SUCCESS
#include <string.h>  // strerror() 
#include <errno.h>

unsigned int i=0;

void*
thread(void* ignore)
{
   printf("i=%i\n", i++);
   return NULL;
}


int
main()
{
   pthread_t tid1, tid2, tid3; // thread 1,2 and 3.
   pthread_attr_t attr;        // thread's attribute
   int rc;  // return code

   while(1)
   {
       rc = pthread_create(&tid1, NULL, thread, NULL);
       rc = pthread_detach(tid1);
       //rc = pthread_create(&tid2, NULL, thread, NULL);
       //rc = pthread_detach(tid2);
       //rc = pthread_create(&tid3, NULL, thread, NULL);
       //rc = pthread_detach(tid3);

       usleep(2000);
   }
   //PthreadCheck("pthread_create", rc);
   //detach_state(tid1, "thread1"); // expect: joinable 
}



