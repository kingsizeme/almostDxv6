#include "types.h"
#include "user.h"
#include "syscall.h"
#include "fcntl.h"
#include "stat.h"


/** System call numbers
#define SYS_fork    1 [CHECK]
#define SYS_exit    2 [CHECK]
#define SYS_wait    3 [CHECK]
#define SYS_pipe    4
#define SYS_read    5
#define SYS_kill    6 [CHECK]
#define SYS_exec    7
#define SYS_fstat   8 [CHECK]
#define SYS_chdir   9 [CHECK]
#define SYS_dup    10 [CHECK]
#define SYS_getpid 11 [CHECK]
#define SYS_sbrk   12 [CHECK]
#define SYS_sleep  13 [CHECK]
#define SYS_uptime 14 [CHECK]
#define SYS_open   15 [CHECK]
#define SYS_write  16 [CHECK]
#define SYS_mknod  17 [CHECK]
#define SYS_unlink 18 [CHECK]
#define SYS_link   19 [CHECK]
#define SYS_mkdir  20 [CHECK]
#define SYS_close  21 [CHECK]
#define SYS_getcount 22 [CHECK]
*/


int
main(int argc, char *argv[])
{
  int pid;
  printf(1, "initial fork count %d\n", getcount(SYS_fork));

  int pdes[2];
 
  pipe(pdes);

  if ((pid=fork()) == 0) {
    printf(1, "child fork count %d\n", getcount(SYS_fork));
    printf(1, "child write count %d\n", getcount(SYS_write));

    int fd;
    int tfd;

    fd = open("testfile.txt",O_RDWR);
    if(fd<0)
      printf(1, "open Dr.zoidberg %d\n", fd);

    struct stat filestat;
    fstat(fd, &filestat);

    printf(1, "child fstat count %d\n", getcount(SYS_fstat));


    tfd = dup(fd);
    write(tfd, "aloha:D", 10);
    if(close(fd) < 0)
      printf(1, "close homer %d\n", close(fd));
    if(close(tfd) < 0)
      printf(1, "close thomer %d\n", close(tfd));

    printf(1, "child dup count %d\n", getcount(SYS_dup));
    printf(1, "child open count %d\n", getcount(SYS_open));
    printf(1, "child close count %d\n", getcount(SYS_close));
    printf(1, "child write count %d\n", getcount(SYS_write));

    link("testfile.txt", "newtestfile.txt");
    unlink("testfile.txt");

    mkdir("/home/testing");
    mknod("/home/testing/trying", 0 , 0);

    printf(1, "child link count %d\n", getcount(SYS_link));
    printf(1, "child unlink count %d\n", getcount(SYS_unlink));
    printf(1, "child mkdir count %d\n", getcount(SYS_mkdir));
    printf(1, "child mknod count %d\n", getcount(SYS_mknod));

    chdir("/home/testing");
    printf(1, "child chdir count %d\n", getcount(SYS_chdir));

    int j = 5;
    while(j>0)
    {
      j--;
      sleep(1);
    }

    printf(1, "child sleep count %d\n", getcount(SYS_sleep));

    unsigned int t;
    t = uptime();
    int thispid;
    thispid = getpid();
    printf(1, "uptime: %d, thispid: %d\n", t,thispid);

    sbrk(4);

    printf(1, "child uptime count %d\n", getcount(SYS_uptime));
    printf(1, "child sbrk count %d\n", getcount(SYS_sbrk));

    kill(pid);
    printf(1, "child kill count %d\n", getcount(SYS_kill));
  } else {
    wait();
    printf(1, "parent fork count %d\n", getcount(SYS_fork));
    printf(1, "parent write count %d\n", getcount(SYS_write));
  }
  printf(1, "wait count %d\n", getcount(SYS_wait));
  exit();
}
