-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 07, 2026 at 07:10 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `nutriscan`
--

-- --------------------------------------------------------

--
-- Table structure for table `ai_analysis`
--

CREATE TABLE `ai_analysis` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `meal_id` int(11) DEFAULT NULL,
  `ai_message` text DEFAULT NULL,
  `recommendation` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ai_analysis`
--

INSERT INTO `ai_analysis` (`id`, `user_id`, `meal_id`, `ai_message`, `recommendation`, `created_at`) VALUES
(1, 1, 8, 'This meal is high in carbohydrates. Fiber content is low. Sodium content is relatively high.', 'Balance the rest of the day with protein and vegetables. Add vegetables, fruit, whole grains or legumes. Choose lower-sodium foods for your next meal.', '2026-09-07 13:30:15'),
(2, 1, 9, 'This meal is high in carbohydrates. Fat content is relatively high. Fiber content is low. Sodium content is relatively high.', 'Balance the rest of the day with protein and vegetables. Keep later meals moderate in added oils and fried foods. Add vegetables, fruit, whole grains or legumes. Choose lower-sodium foods for your next meal.', '2026-09-07 13:34:30'),
(3, 1, 10, '[Health Score: 66/100 - Balanced] Pizza provides 520 kcal with 20.0g protein.', 'Maintain meal balance by staying hydrated and keeping sodium moderate. Sodium is high. Drink plenty of water and choose low-sodium foods for your next meal.', '2026-09-07 16:00:22'),
(4, 1, 11, '[Health Score: 66/100 - Balanced] Pizza provides 520 kcal with 20.0g protein.', 'Maintain meal balance by staying hydrated and keeping sodium moderate. Sodium is high. Drink plenty of water and choose low-sodium foods for your next meal.', '2026-09-07 16:45:22'),
(5, 1, 12, '[Health Score: 80/100 - Very Healthy] Chicken Biryani provides 520 kcal with 20.0g protein.', 'Maintain meal balance by staying hydrated and keeping sodium moderate. Sodium is high. Drink plenty of water and choose low-sodium foods for your next meal.', '2026-09-07 16:45:22');

-- --------------------------------------------------------

--
-- Table structure for table `daily_goals`
--

CREATE TABLE `daily_goals` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `calorie_goal` float DEFAULT 2000,
  `protein_goal` float DEFAULT 60,
  `carb_goal` float DEFAULT 250,
  `fat_goal` float DEFAULT 65,
  `fiber_goal` float DEFAULT 30
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `food_items`
--

CREATE TABLE `food_items` (
  `id` int(11) NOT NULL,
  `food_name` varchar(100) NOT NULL,
  `serving_size` varchar(50) DEFAULT NULL,
  `calories` float DEFAULT 0,
  `protein` float DEFAULT 0,
  `carbohydrates` float DEFAULT 0,
  `fat` float DEFAULT 0,
  `fiber` float DEFAULT 0,
  `sugar` float DEFAULT 0,
  `sodium` float DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `food_items`
--

INSERT INTO `food_items` (`id`, `food_name`, `serving_size`, `calories`, `protein`, `carbohydrates`, `fat`, `fiber`, `sugar`, `sodium`) VALUES
(1, 'Poha', '1 bowl (150g)', 250, 5, 40, 8, 3, 2, 350),
(2, 'Idli', '2 pieces (120g)', 150, 5, 30, 1, 2, 1, 300),
(3, 'Dosa', '1 medium (100g)', 170, 4, 28, 5, 2, 1, 250),
(4, 'Chapati', '2 pieces (80g)', 160, 6, 30, 3, 4, 1, 180),
(5, 'Dal Rice', '1 plate (300g)', 400, 14, 65, 8, 8, 3, 400),
(6, 'Biryani', '1 plate (300g)', 520, 20, 65, 18, 4, 4, 700),
(7, 'Vada Pav', '1 piece', 290, 7, 40, 11, 3, 5, 550),
(8, 'Pav Bhaji', '1 plate', 400, 10, 55, 15, 7, 6, 650),
(9, 'Upma', '1 bowl (200g)', 220, 6, 35, 7, 4, 2, 300),
(10, 'Samosa', '2 pieces', 260, 6, 30, 13, 3, 2, 450),
(11, 'Paneer Tikka', '150g', 320, 22, 10, 22, 2, 3, 500),
(12, 'Rajma Rice', '1 plate (300g)', 420, 15, 70, 9, 10, 4, 450),
(13, 'biryani', '1 plate', 450, 22, 55, 16, 3, 4, 700),
(14, 'pizza', '2 slices', 520, 20, 58, 24, 3, 6, 900),
(15, 'burger', '1 burger', 450, 25, 40, 22, 3, 7, 800),
(16, 'pasta', '1 bowl', 380, 14, 55, 12, 4, 6, 500),
(17, 'fried rice', '1 plate', 400, 10, 60, 14, 3, 5, 650),
(18, 'idli', '2 pieces', 140, 5, 28, 1, 2, 1, 300),
(19, 'dosa', '1 dosa', 170, 4, 30, 4, 2, 1, 350);

-- --------------------------------------------------------

--
-- Table structure for table `meal_history`
--

CREATE TABLE `meal_history` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `food_id` int(11) DEFAULT NULL,
  `food_name` varchar(100) NOT NULL,
  `quantity` float DEFAULT 1,
  `calories` float DEFAULT 0,
  `protein` float DEFAULT 0,
  `carbohydrates` float DEFAULT 0,
  `fat` float DEFAULT 0,
  `fiber` float DEFAULT 0,
  `image_path` varchar(255) DEFAULT NULL,
  `meal_type` varchar(30) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `meal_history`
--

INSERT INTO `meal_history` (`id`, `user_id`, `food_id`, `food_name`, `quantity`, `calories`, `protein`, `carbohydrates`, `fat`, `fiber`, `image_path`, `meal_type`, `created_at`) VALUES
(1, 1, 6, 'chicken biryani', 1, 520, 20, 65, 18, 4, 'uploads\\biryani.jpg', 'Meal', '2026-09-06 17:25:17'),
(2, 1, 6, 'chicken biryani', 1, 520, 20, 65, 18, 4, 'uploads\\biryani.jpg', 'Meal', '2026-09-06 17:43:19'),
(3, 1, 6, 'chicken biryani', 1, 520, 20, 65, 18, 4, 'uploads\\biryani.jpg', 'Meal', '2026-09-06 18:24:18'),
(4, 1, 6, 'chicken biryani', 1, 520, 20, 65, 18, 4, 'uploads\\biryani.jpg', 'Meal', '2026-09-06 18:25:31'),
(5, 1, 6, 'chicken biryani', 1, 520, 20, 65, 18, 4, 'uploads\\biryani.jpg', 'Meal', '2026-09-06 18:25:44'),
(6, 1, 6, 'chicken biryani', 1, 520, 20, 65, 18, 4, 'uploads\\biryani.jpg', 'Meal', '2026-09-06 18:36:16'),
(7, 1, 6, 'chicken biryani', 1, 520, 20, 65, 18, 4, 'uploads\\biryani.jpg', 'Meal', '2026-09-06 18:40:53'),
(8, 1, 6, 'chicken biryani', 1, 520, 20, 65, 18, 4, 'uploads\\biryani.jpg', 'Meal', '2026-09-07 13:30:15'),
(9, 1, 14, 'pizza', 1, 520, 20, 58, 24, 3, 'uploads\\pizza.jpg', 'Meal', '2026-09-07 13:34:30'),
(10, 1, 14, 'Pizza', 1, 520, 20, 58, 24, 3, 'uploads\\pizza.jpg', 'Lunch', '2026-09-07 16:00:22'),
(11, 1, 14, 'Pizza', 1, 520, 20, 58, 24, 3, 'uploads\\pizza_1_1788799506552.jpg', 'Lunch', '2026-09-07 16:45:22'),
(12, 1, 6, 'Chicken Biryani', 1, 520, 20, 65, 18, 4, 'uploads\\camera_capture_1_1788799522448.jpg', 'Dinner', '2026-09-07 16:45:22');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `age` int(11) DEFAULT NULL,
  `height` float DEFAULT NULL,
  `weight` float DEFAULT NULL,
  `gender` varchar(20) DEFAULT NULL,
  `activity_level` varchar(30) DEFAULT NULL,
  `goal` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `age`, `height`, `weight`, `gender`, `activity_level`, `goal`, `created_at`) VALUES
(1, 'Pr Pote College', 'prpotec3@gmail.com', 'scrypt:32768:8:1$xGvqk7meudoqaN23$ddae1fde9e4dc4fe496ad35401ffbff092f754f7d73acd3be31cf0ca5a70f787adc5b85580356ed38e2534bb5f1dee7424de1bbb2675a7635103798464f28d46', 19, 172, 70, 'Male', 'Moderately Active', 'Maintain Weight', '2026-09-05 20:25:57');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ai_analysis`
--
ALTER TABLE `ai_analysis`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `meal_id` (`meal_id`);

--
-- Indexes for table `daily_goals`
--
ALTER TABLE `daily_goals`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `food_items`
--
ALTER TABLE `food_items`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `meal_history`
--
ALTER TABLE `meal_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `food_id` (`food_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ai_analysis`
--
ALTER TABLE `ai_analysis`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `daily_goals`
--
ALTER TABLE `daily_goals`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `food_items`
--
ALTER TABLE `food_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `meal_history`
--
ALTER TABLE `meal_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `ai_analysis`
--
ALTER TABLE `ai_analysis`
  ADD CONSTRAINT `ai_analysis_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `ai_analysis_ibfk_2` FOREIGN KEY (`meal_id`) REFERENCES `meal_history` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `daily_goals`
--
ALTER TABLE `daily_goals`
  ADD CONSTRAINT `daily_goals_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `meal_history`
--
ALTER TABLE `meal_history`
  ADD CONSTRAINT `meal_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `meal_history_ibfk_2` FOREIGN KEY (`food_id`) REFERENCES `food_items` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
