-- MySQL dump 10.14  Distrib 5.5.47-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: bsyops
-- ------------------------------------------------------
-- Server version	5.5.47-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `bsyops`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `bsyops` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `bsyops`;

--
-- Table structure for table `ops_PreProd`
--

DROP TABLE IF EXISTS `ops_PreProd`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ops_PreProd` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `IP` varchar(15) NOT NULL,
  `ServiceName` varchar(20) NOT NULL,
  `WebApps` varchar(200) NOT NULL,
  `ReleaseName` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ops_deployLog`
--

DROP TABLE IF EXISTS `ops_deployLog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ops_deployLog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `operator` varchar(20) NOT NULL,
  `startTime` datetime NOT NULL,
  `completeTime` datetime NOT NULL,
  `deployService` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ops_env`
--

DROP TABLE IF EXISTS `ops_env`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ops_env` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `EnvName` varchar(20) NOT NULL,
  `GroupId` tinyint(4) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ops_project`
--

DROP TABLE IF EXISTS `ops_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ops_project` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `ProjectName` varchar(10) NOT NULL,
  `GroupId` tinyint(4) NOT NULL,
  `ServiceId` tinyint(4) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ops_server`
--

DROP TABLE IF EXISTS `ops_server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ops_server` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `IP` varchar(15) NOT NULL,
  `GroupId` tinyint(4) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ops_service`
--

DROP TABLE IF EXISTS `ops_service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ops_service` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `ServiceName` varchar(10) NOT NULL,
  `GroupId` tinyint(4) NOT NULL,
  `ServiceId` tinyint(4) NOT NULL,
  `WebApps` varchar(200) NOT NULL,
  `ReleaseName` varchar(100) NOT NULL,
  `EnvId` tinyint(4) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ops_user`
--

DROP TABLE IF EXISTS `ops_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ops_user` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `UserName` varchar(40) NOT NULL,
  `FullName` varchar(40) DEFAULT NULL,
  `Password` varchar(200) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `DepartmentName` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-09-22 15:51:34
