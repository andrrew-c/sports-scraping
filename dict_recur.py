
## Recursive solution to update a nested dictionary
def update(current, new):
    import collections 
    ## For key, value in the new updating dictionary
    for k, v in new.items():
        
        ## If the value of the key is a dictioanry then update that dictionary with the value
        if isinstance(v, collections.Mapping):
            
            ## Recursive - aims to update the next dictionary down, with the value from U (new)
            r = update(current.get(k, {}), v)

            ## update d with updated r
            current[k] = r
        else:
            ## Update dictionary d[key] with updated[key]
            current[k] = new[k]
            
    return current
