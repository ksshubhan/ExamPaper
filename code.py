class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        l, r = 0, len(numbers) - 1
        total = 0
        total = numbers[l] + numbers[r]
        while total != target:
            # if the total is greater than target
            if total > target:
                # then shift the right pointer down 1 
                r -= 1
            # if the total is less than target 
            elif total < target:
                # then shift the left pointer down 1 
                l += 1
            else:
                break
            total = numbers[l] + numbers[r]

        # remember array is 1-indexed so need to offset coordinates by 1
        return [l + 1, r + 1]