CREATE TABLE IF NOT EXISTS parts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    quantity INTEGER NOT NULL CHECK (quantity >= 0) DEFAULT 0,
    category TEXT NOT NULL,
    location TEXT NOT NULL
);
-- I could add another table just for categories and add a FK for it but for simplicty I won't do this for that task
-- I added unique to name as I don't want a name to be repeated since the LLM will use function calling and seeing two names in the column can result in unpredictable answers
-- for location I added not null assuming that each part has a specfic location and doesn't change a lot so when quantity is 0 location isn't very misleading so when we have parts we know where to put them

INSERT INTO parts (name, quantity, category, location) VALUES
('Brake Disc', 8, 'Brakes', 'Shelf A1'),
('Brake Pad Set', 12, 'Brakes', 'Shelf A2'),
('Wheel Bearing', 16, 'Suspension', 'Shelf B1'),
('Tie Rod End', 10, 'Steering', 'Shelf B2'),
('Steering Rack', 2, 'Steering', 'Rack C1'),
('Control Arm', 8, 'Suspension', 'Rack C2'),
('CV Joint', 6, 'Drivetrain', 'Shelf D1'),
('Drive Shaft', 4, 'Drivetrain', 'Rack D2'),
('Spark Plug', 20, 'Engine', 'Shelf E1'),
('Oil Filter', 15, 'Engine', 'Shelf E2');