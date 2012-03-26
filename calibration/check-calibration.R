cal <- read.table('20120326-speed.txt',header=TRUE)

library(ggplot2)
fig1 <- ggplot(data=cal,aes(byte,speed.mps))+geom_point()+geom_smooth()

foo <- lm(speed.mps~byte,data=cal)
summary(foo)

pdf("calibration.pdf",width=5,height=5)
print(foo)
dev.off()

