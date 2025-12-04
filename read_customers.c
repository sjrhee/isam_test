/***************************************************************************
 *
 *                   C-ISAM Customer Management System
 *
 *  Title:  read_customers.c
 *  Description:
 *      This program sequentially reads customer records from ISAM file
 *      and displays them on the screen.
 *
 ***************************************************************************/
#include <isam.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define WHOLEKEY 0
#define SUCCESS 0
#define CUSTOMER_FILE "customers.isam"
#define RECLEN 185
#define TRUE 1
#define FALSE 0

char custrec[RECLEN];
int eof = FALSE;

struct keydesc key;
int fd, cc;

/*
   This program sequentially reads through the customer
   file displaying each record
*/
main()
{
   int record_count = 0;

   printf("Opening ISAM file: %s\n\n", CUSTOMER_FILE);

   fd = cc = isopen(CUSTOMER_FILE, ISMANULOCK + ISINOUT);
   if (cc < SUCCESS)
   {
      printf("isopen error %d for customer file\n", iserrno);
      exit(1);
   }

   /* Set File to Retrieve using customer_id Index */
   key.k_flags = ISDUPS;
   key.k_nparts = 1;
   key.k_part[0].kp_start = 0;
   key.k_part[0].kp_leng = 4;
   key.k_part[0].kp_type = LONGTYPE;
   cc = isstart(fd, &key, WHOLEKEY, custrec, ISFIRST);
   if (cc != SUCCESS)
   {
      printf("isstart error %d\n", iserrno);
      isclose(fd);
      exit(1);
   }

   printf("========================================\n");
   printf("Customer Records from ISAM File\n");
   printf("========================================\n\n");

   getfirst();
   while (!eof)
   {
      showcustomer();
      getnext();
      record_count++;

      if (record_count >= 20)
      {
         printf("... (showing first 20 records)\n\n");
         break;
      }
   }

   /* Count total records */
   isstart(fd, &key, WHOLEKEY, custrec, ISFIRST);
   int total_count = 0;
   while (isread(fd, custrec, ISNEXT) >= 0)
   {
      total_count++;
   }

   printf("========================================\n");
   printf("Total records: %d\n", total_count);
   printf("========================================\n\n");

   isclose(fd);
   return 0;
}

showcustomer()
{
   printf("ID: %d | Name: ", ldlong(custrec));
   my_putnc(custrec+4, 50);
   printf(" | Email: ");
   my_putnc(custrec+54, 30);
   printf("\n     Phone: ");
   my_putnc(custrec+154, 20);
   printf(" | Date: ");
   my_putnc(custrec+174, 10);
   printf("\n\n");
}

my_putnc(c, n)
char *c;
int n;
{
   while (n--) putchar(*(c++));
}

getfirst()
{
   int cc;

   if (cc = isread(fd, custrec, ISFIRST))
   {
      switch(iserrno)
      {
         case EENDFILE:
            eof = TRUE;
            break;
         default:
            printf("isread ISFIRST error %d\n", iserrno);
            eof = TRUE;
            return(1);
      }
   }
   return(0);
}

getnext()
{
   int cc;

   if (cc = isread(fd, custrec, ISNEXT))
   {
      switch(iserrno)
      {
         case EENDFILE:
            eof = TRUE;
            break;
         default:
            printf("isread ISNEXT error %d\n", iserrno);
            eof = TRUE;
            return(1);
      }
   }
   return(0);
}
