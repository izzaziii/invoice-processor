# MongoDB Find & Filter Cheat Sheet

## Basic Find Operations

1. **Find all documents**
```javascript
db.invoices.find({})
```

2. **Find with exact match**
```javascript
db.invoices.find({ "invoice_details.invoice_number": "INV-12345" })
```

3. **Find with multiple conditions (AND)**
```javascript
db.invoices.find({
    "invoice_details.invoice_date": "2024-02-23",
    "invoice_details.total_cost": "5000.00"
})
```

4. **Find with OR condition**
```javascript
db.invoices.find({
    $or: [
        { "campaign_details.platform": "Meta" },
        { "campaign_details.platform": "Google" }
    ]
})
```

5. **Find with IN operator**
```javascript
db.invoices.find({
    "campaign_details.funnel_stage": {
        $in: ["awareness", "consideration"]
    }
})
```

## Comparison Operators

6. **Greater than**
```javascript
db.invoices.find({
    "invoice_details.total_cost": { $gt: "1000.00" }
})
```

7. **Less than or equal**
```javascript
db.invoices.find({
    "invoice_details.total_cost": { $lte: "5000.00" }
})
```

8. **Not equal**
```javascript
db.invoices.find({
    "campaign_details.language": { $ne: "English" }
})
```

## Array Operations

9. **Find documents with array containing element**
```javascript
db.invoices.find({
    "line_items.platform": "Meta"
})
```

10. **Find with array size**
```javascript
db.invoices.find({
    "line_items": { $size: 2 }
})
```

## Regular Expressions

11. **Find with regex pattern**
```javascript
db.invoices.find({
    "invoice_details.invoice_number": /^INV-/
})
```

## Field Existence

12. **Check if field exists**
```javascript
db.invoices.find({
    "campaign_details.end_date": { $exists: true }
})
```

## Limiting & Sorting

13. **Limit results**
```javascript
db.invoices.find({}).limit(5)
```

14. **Sort results (1 ascending, -1 descending)**
```javascript
db.invoices.find({}).sort({ "invoice_details.invoice_date": -1 })
```

## Projection (Field Selection)

15. **Select specific fields**
```javascript
db.invoices.find(
    {},
    { "invoice_details.invoice_number": 1, "invoice_details.total_cost": 1 }
)
```

## Complex Queries

16. **Nested AND/OR conditions**
```javascript
db.invoices.find({
    $and: [
        { "campaign_details.platform": "Meta" },
        { $or: [
            { "campaign_details.funnel_stage": "awareness" },
            { "campaign_details.funnel_stage": "consideration" }
        ]}
    ]
})
```

17. **Find with date range**
```javascript
db.invoices.find({
    "invoice_details.invoice_date": {
        $gte: "2024-01-01",
        $lte: "2024-12-31"
    }
})
```

18. **Find with array element match**
```javascript
db.invoices.find({
    "line_items": {
        $elemMatch: {
            "platform": "Meta",
            "funnel_stage": "awareness"
        }
    }
})
```

19. **Count documents with condition**
```javascript
db.invoices.countDocuments({
    "campaign_details.platform": "Meta"
})
```

20. **Distinct values**
```javascript
db.invoices.distinct("campaign_details.platform")
```

## Bonus: Common Pipeline Aggregation

```javascript
db.invoices.aggregate([
    // Match stage
    { $match: { "campaign_details.platform": "Meta" } },
    // Group stage
    { $group: {
        _id: "$campaign_details.funnel_stage",
        total_cost: { $sum: { $toDouble: "$invoice_details.total_cost" } },
        count: { $sum: 1 }
    }},
    // Sort stage
    { $sort: { total_cost: -1 } }
])
```
