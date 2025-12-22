def remove_fields(s, fields):
    for field in fields:
        s = s.replace(field, '')
    return s

# 示例
s = "%u12U4E3A%u12U4EC0%u12U4E48%u12U6211%u12U53D1%u12U7535%u12U62A5%u12U603B%u12U662F%u12U6CA1%u12U4EBA%u12U56DE%u12U5E94%u12UFF0C%u12U8FD9%u12U5230%u12U5E95%u12U662F%u12U4E3A%u12U4EC0%u12U4E48%u12UFF1F%u12U6C42%u12U544A%u12U77E5%u12U6C42%u12U544A%u12U77E5"
fields = ["12U"]
result = remove_fields(s, fields)
print(result)
