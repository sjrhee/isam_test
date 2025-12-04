/***************************************************************************
 *
 *                   C-ISAM Customer Management System
 *
 *  Title:  load_customers.c
 *  Description:
 *      This program loads customer data from CSV file into C-ISAM file.
 *      It creates an indexed sequential file with customer_id as primary key.
 *
 ***************************************************************************/
#include <isam.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define WHOLEKEY 0
#define SUCCESS 0
#define CUSTOMER_FILE "customers.isam"
#define CSV_FILE "customers.csv"
#define RECLEN 185

char custrec[RECLEN];
char line[300];
int cust_id;

struct keydesc key;
int fd, cc;

static void parsecsvrecord(char *src, int *id, char *name, char *email, 
                          char *phone, char *regdate);
static void ststring(char *src, char *dest, int num);

/*
   This program loads customer records from CSV file to ISAM file
*/
main()
{
   FILE *csv_fp;
   int record_count = 0;
   int error_count = 0;
   char name[51], email[101], phone[21], regdate[12];

   printf("Creating ISAM file: %s\n", CUSTOMER_FILE);

   /* Delete existing file */
   unlink(CUSTOMER_FILE);

   /* Set up Customer Key - customer_id (LONGTYPE) */
   key.k_flags = ISDUPS;
   key.k_nparts = 1;
   key.k_part[0].kp_start = 0;
   key.k_part[0].kp_leng = 4;
   key.k_part[0].kp_type = LONGTYPE;

   fd = cc = isbuild(CUSTOMER_FILE, RECLEN, &key, ISINOUT + ISEXCLLOCK);
   if (cc < SUCCESS)
   {
      printf("isbuild error %d\n", iserrno);
      exit(1);
   }
   isclose(fd);

   /* Open CSV file for reading */
   csv_fp = fopen(CSV_FILE, "r");
   if (csv_fp == NULL)
   {
      printf("Cannot open CSV file: %s\n", CSV_FILE);
      exit(1);
   }

   /* Skip header line */
   if (fgets(line, sizeof(line), csv_fp) == NULL)
   {
      printf("Cannot read CSV header\n");
      fclose(csv_fp);
      exit(1);
   }

   /* Open ISAM file for writing */
   fd = isopen(CUSTOMER_FILE, ISAUTOLOCK + ISOUTPUT);
   if (fd < SUCCESS)
   {
      printf("isopen error %d for customer file\n", iserrno);
      fclose(csv_fp);
      exit(1);
   }

   printf("Loading data from %s...\n", CSV_FILE);

   /* Read and write records */
   while (fgets(line, sizeof(line), csv_fp) != NULL)
   {
      /* Clear record */
      memset(custrec, ' ', RECLEN);

      /* Parse CSV record */
      parsecsvrecord(line, &cust_id, name, email, phone, regdate);

      if (cust_id == 0)
         continue;

      /* Build ISAM record */
      stlong(cust_id, custrec);
      ststring(name, custrec+4, 50);
      ststring(email, custrec+54, 100);
      ststring(phone, custrec+154, 20);
      ststring(regdate, custrec+174, 11);

      /* Write record */
      cc = iswrite(fd, custrec);
      if (cc != SUCCESS)
      {
         printf("iswrite error %d for customer_id %d\n", iserrno, cust_id);
         error_count++;
      }
      else
      {
         record_count++;
         if (record_count % 100 == 0)
            printf("  Loaded %d records...\n", record_count);
      }
   }

   fclose(csv_fp);
   isclose(fd);

   printf("\n========================================\n");
   printf("Loading completed!\n");
   printf("Total records loaded: %d\n", record_count);
   printf("Errors: %d\n", error_count);
   printf("ISAM file: %s\n", CUSTOMER_FILE);
   printf("========================================\n");

   return 0;
}

/* Parse CSV record */
static void parsecsvrecord(char *src, int *id, char *name, char *email,
                          char *phone, char *regdate)
{
   char *ptr;
   char line_copy[300];

   strcpy(line_copy, src);
   line_copy[strcspn(line_copy, "\n")] = 0;

   ptr = strtok(line_copy, ",");
   *id = (ptr != NULL) ? atoi(ptr) : 0;

   ptr = strtok(NULL, ",");
   strcpy(name, (ptr != NULL) ? ptr : "");

   ptr = strtok(NULL, ",");
   strcpy(email, (ptr != NULL) ? ptr : "");

   ptr = strtok(NULL, ",");
   strcpy(phone, (ptr != NULL) ? ptr : "");

   ptr = strtok(NULL, ",");
   strcpy(regdate, (ptr != NULL) ? ptr : "");
}

/* Move sequential characters from src to dest */
static void ststring(char *src, char *dest, int num)
{
   int i;
   for (i = 1; i <= num && *src != '\n' && *src != 0; i++)
      *dest++ = *src++;
   while (i++ <= num)
      *dest++ = ' ';
}
