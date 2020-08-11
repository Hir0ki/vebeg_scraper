CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    is_top_level BOOLEAN NOT NULL,
    parent_id INTEGER
);
CREATE TABLE IF NOT EXISTS Listings (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    data JSONB,
    kurzbeschreibung TEXT NOT NULL,
    gebotsbasis VARCHAR(500),
    lagerort TEXT NOT NULL,
    gebotstermin DATE,
    category_id INTEGER NOT NULL,
    sold_price INTEGER,
    CONSTRAINT fk_category
        FOREIGN KEY(category_id) 
	    REFERENCES Categories(id)
);

