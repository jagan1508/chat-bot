-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: jagandb
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `employee`
--

DROP TABLE IF EXISTS `employee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee` (
  `EmployeeID` int NOT NULL,
  `EmployeeName` varchar(255) NOT NULL,
  `DateOfJoining` date NOT NULL,
  `EmployeeType` varchar(255) DEFAULT NULL,
  `PayTier` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`EmployeeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employee`
--

LOCK TABLES `employee` WRITE;
/*!40000 ALTER TABLE `employee` DISABLE KEYS */;
INSERT INTO `employee` VALUES (1,'John Doe','2023-01-15','Manager','Tier 1'),(2,'Jane Smith','2022-06-01','Engineer-1','Tier 3'),(3,'Alice Johnson','2021-09-12','Tester','Tier 4'),(4,'Bob Brown','2020-03-23','Engineer-2','Tier 2'),(5,'Charlie Davis','2023-07-08','Team Lead','Tier 1'),(6,'Eve Martin','2019-11-05','Engineer-1','Tier 3'),(7,'Frank White','2022-02-17','Tester','Tier 4'),(8,'Grace Green','2021-08-30','Manager','Tier 1'),(9,'Hank Lee','2020-12-19','Engineer-2','Tier 2'),(10,'Ivy Wilson','2023-03-11','Team Lead','Tier 1'),(11,'Jack Black','2022-05-25','Engineer-1','Tier 3'),(12,'Karen Scott','2021-07-14','Tester','Tier 4'),(13,'Larry Adams','2020-09-01','Engineer-2','Tier 2'),(14,'Mona Young','2019-04-22','Manager','Tier 1'),(15,'Nate King','2023-10-10','Team Lead','Tier 1'),(16,'Olivia Perry','2023-02-10','Manager','Tier 1'),(17,'Liam Gray','2022-11-15','Engineer-1','Tier 3'),(18,'Sophia Reed','2021-05-20','Engineer-2','Tier 2'),(19,'James Ward','2020-08-10','Tester','Tier 4'),(20,'Charlotte Hall','2023-06-25','Team Lead','Tier 1'),(21,'Benjamin Lewis','2022-01-13','Manager','Tier 1'),(22,'Amelia Foster','2021-10-30','Engineer-1','Tier 3'),(23,'Ethan Scott','2020-04-19','Engineer-2','Tier 2'),(24,'Isabella Clark','2019-09-01','Tester','Tier 4'),(25,'Lucas King','2023-03-14','Team Lead','Tier 1'),(26,'Mia Lopez','2022-07-20','Manager','Tier 1'),(27,'Noah Adams','2021-02-28','Engineer-1','Tier 3'),(28,'Emma Turner','2020-12-09','Engineer-2','Tier 2'),(29,'Ava Martin','2023-05-22','Tester','Tier 4'),(30,'Oliver Davis','2022-08-11','Team Lead','Tier 1'),(31,'Harper Wilson','2021-03-17','Manager','Tier 1'),(32,'Elijah Robinson','2020-06-08','Engineer-1','Tier 3'),(33,'Abigail Carter','2019-11-05','Engineer-2','Tier 2'),(34,'Henry Mitchell','2023-01-09','Tester','Tier 4'),(35,'Emily Perez','2022-04-29','Team Lead','Tier 1'),(36,'Ella Morgan','2021-08-27','Manager','Tier 1'),(37,'Jackson Kelly','2020-02-14','Engineer-1','Tier 3'),(38,'Chloe White','2019-05-19','Engineer-2','Tier 2'),(39,'William Harris','2023-09-07','Tester','Tier 4'),(40,'Sofia Baker','2022-10-12','Team Lead','Tier 1'),(41,'Aiden Rivera','2021-11-03','Manager','Tier 1'),(42,'Grace Torres','2020-07-25','Engineer-1','Tier 3'),(43,'Ella Foster','2019-12-31','Engineer-2','Tier 2'),(44,'Daniel Gonzalez','2023-04-18','Tester','Tier 4'),(45,'Victoria Ramirez','2022-03-22','Team Lead','Tier 1'),(46,'Matthew Powell','2021-01-16','Manager','Tier 1'),(47,'Scarlett Bennett','2020-09-29','Engineer-1','Tier 3'),(48,'Avery Sanders','2019-06-07','Engineer-2','Tier 2'),(49,'Levi Jenkins','2023-08-21','Tester','Tier 4'),(50,'Eleanor Ross','2022-02-06','Team Lead','Tier 1');
/*!40000 ALTER TABLE `employee` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-09 17:04:54
