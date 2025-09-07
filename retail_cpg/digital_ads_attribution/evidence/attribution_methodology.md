# Attribution Methodology Guide

## Attribution Models Overview

### First-Touch Attribution
- **Use Case**: Brand awareness campaigns, top-of-funnel analysis
- **Methodology**: 100% credit to first interaction
- **Best For**: Understanding acquisition channels
- **Limitations**: Ignores nurturing touchpoints

### Last-Touch Attribution  
- **Use Case**: Direct response campaigns, conversion optimization
- **Methodology**: 100% credit to final interaction before conversion
- **Best For**: Optimizing closing tactics
- **Limitations**: Undervalues awareness and consideration phases

### Linear Attribution
- **Use Case**: Full-funnel understanding, balanced view
- **Methodology**: Equal credit distributed across all touchpoints
- **Best For**: Understanding complete customer journey
- **Limitations**: May overvalue low-impact touchpoints

### Time-Decay Attribution
- **Use Case**: Sales-focused campaigns with longer cycles
- **Methodology**: More credit to recent interactions (exponential decay)
- **Best For**: B2B or high-consideration purchases
- **Configuration**: 7-day half-life (50% credit decay)

### Position-Based Attribution (U-Shaped)
- **Use Case**: Balanced brand and performance focus
- **Methodology**: 40% first touch, 40% last touch, 20% distributed
- **Best For**: Multi-stage marketing funnels
- **Ideal For**: Retail and ecommerce

### Data-Driven Attribution
- **Use Case**: High-volume, sophisticated attribution
- **Methodology**: Machine learning based on conversion patterns
- **Requirements**: 15,000+ conversions and 600+ conversion paths per month
- **Best For**: Large-scale digital advertising

## Implementation Guidelines

### Attribution Window Settings
- **Default Window**: 7 days (168 hours)
- **View-Through Window**: 1 day (24 hours)
- **Cross-Device**: Enabled with user login tracking
- **Lookback Period**: 30 days for analysis

### Platform-Specific Considerations
- **Google Ads**: Data-driven when volume permits, otherwise time-decay
- **Facebook/Instagram**: 7-day click, 1-day view
- **Amazon**: Last-touch (platform limitation)
- **LinkedIn**: Position-based for B2B campaigns

### Reporting Standards
- **Primary Model**: Time-decay for optimization decisions
- **Secondary Model**: Linear for budget allocation
- **Comparison Reports**: Show multiple models side-by-side
- **Update Frequency**: Daily for tactical, weekly for strategic

## Quality Assurance

### Data Validation Checks
- Touchpoint timestamp accuracy
- User ID consistency across platforms
- Conversion value validation
- Attribution window compliance

### Performance Monitoring
- Model performance comparison
- Conversion path analysis
- Cross-platform journey validation
- Attribution lift testing
