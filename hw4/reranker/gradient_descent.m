clear all
close all


%% gradient descent
alpha = 0.99;
n=5;
resolution = 0.05;
[o_x,o_y,o_z] = meshgrid(-1:1,-1:1,-1:1);
offset = [reshape(o_x,27,1) reshape(o_y,27,1) reshape(o_z,27,1)]*resolution;

theta_seed = [-5.625 -3.125 -7.125]+rand;
cmd = ['./rerank -l ' num2str(theta_seed(1))...
            ' -t ' num2str(theta_seed(2))...
            ' -s ' num2str(theta_seed(3))...
            '| ./compute-bleu'];
[status, val] = system(cmd);
biggest = str2double(val);
prev_biggest = biggest;
term_flag = false;
changed_res = false;
num_bytes = 0;
max_iter = 20;
iter = 1;
bad_operation = false;
thetas = [theta_seed];
figure(1)
clf
h=plot3(thetas(1),thetas(2),thetas(3),'r-');
hold on
plot3(thetas(1),thetas(2),thetas(3),'g*');
grid on
axis equal
while ~term_flag && iter <= max_iter && ~bad_operation
    % generate new parameters
    theta = bsxfun(@plus,theta_seed,offset);
    bleu_score = zeros(size(theta,1),1);
    
    % calculate BLEU score for each set of parameters
    for i = 1:length(bleu_score)
        cmd = ['./rerank -l ' num2str(theta(i,1))...
            ' -t ' num2str(theta(i,2))...
            ' -s ' num2str(theta(i,3))...
            '| ./compute-bleu'];
        [status, score] = system(cmd);
        if status
            bad_operation = true;
        end
        bleu_score(i) = str2double(score);
    end
    
    % find the best calculated score
    [biggest,idx] = max(bleu_score);
    error = biggest - prev_biggest;
    (theta(idx,:)-theta_seed)
    dtheta = alpha*error./(theta(idx,:)-theta_seed);
    dtheta(isnan(dtheta) | isinf(dtheta)) = 0;
    theta_seed = theta_seed + dtheta;
    thetas = [thetas; theta_seed];
    set(h,'xdata',thetas(:,1),'ydata',thetas(:,2),'zdata',thetas(:,3))
    drawnow
    if abs(prev_biggest - biggest) < 1e-9
        term_flag = true;
    end
    %fprintf(repmat('\b',1,num_bytes));
    num_bytes = fprintf('iteration: %d | BLEU score: %6.6f | parameters: %6.6f %6.6f %6.6f\n',...
        iter, biggest, theta(idx,1), theta(idx,2), theta(idx,3));
    
    prev_biggest = biggest;
    iter = iter+1;
end
fprintf('\n')